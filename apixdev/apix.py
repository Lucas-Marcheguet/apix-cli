
import os
import logging
import tempfile
from zipfile import ZipFile
import sh
import sys


import getpass
import gitlab

import apixdev.config as cfg
from apixdev.cli.tools import dict_to_string
from apixdev.repository import GitRepository
from apixdev.common import SingletonMeta, Config, Odoo
from apixdev.compose import Commpose

_logger = logging.getLogger(__name__)




class Apix(metaclass=SingletonMeta):

    _odoo = None
    _path = ""

    def __init__(self):
        _logger.info('ApiX running')

        path = os.path.join(os.environ['HOME'], cfg.CONFIG_PATH)
        self.config = Config(path)

    
    @property
    def odoo_credentials(self):
        return [
            self.config.get_var('apix.url'), 
            self.config.get_var('apix.database'), 
            self.config.get_var('apix.user'), 
            self.config.get_var('apix.password'), 
        ]
        
    @property
    def odoo_options(self):
        return {k:self.config.get_var("apix.%s" % k) for k in cfg.ODOORPC_OPTIONS}

    @property
    def odoo(self):
        return Odoo(*self.odoo_credentials, **self.odoo_options)


    def set_config(self):
        while not self.is_ready:
            vals = dict()
            for key, value in self.config.get_missing_values():
                if 'password' in key:
                    vals[key] = getpass.getpass("{}: ".format(key.capitalize()))
                else:
                    vals[key] = input("{}: ".format(key.capitalize()))
            self.config.set_vars(vals)        
        

    @property
    def is_ready(self):
        return True if self.config and len(self.config.get_missing_values()) == 0 else False        



    def check_project(self, name):
        project_path = self.get_project_path(name)

        if not os.path.exists(project_path):
            return False

        content = os.listdir(project_path)

        required = ['docker-compose.yaml', 'repositories']

        if len(list(set(content).union(set(required)))) != len(required):
            return False

        # if not 'docker-compose.yml' in content:
        #     return False
        
        # if not 'repositories' in content:
        #     return False

        return True

    
    def get_local_projects(self):
        workdir_path = self.config.get_var('local.workdir')
        if not os.path.isdir(workdir_path):
            os.makedirs(workdir_path)

        # projects = [dir for dir in os.listdir(workdir_path) if self.check_project(dir)]
        projects = list(filter(self.check_project, os.listdir(workdir_path)))
        projects.sort()

        return projects

    def get_gitlab_project(self, name):
        gl = gitlab.Gitlab(
            url=self.config.get_var('git.remote_url'), 
            private_token=self.config.get_var('git.remote_token'))

        project = gl.projects.get(name)
        return project        


    def scaffold_module(self, name):
        project = self.get_gitlab_project(self.config.get_var('scaffold.odoo-template'))

        # tmp = tempfile.NamedTemporaryFile('wb')
        exclude = ['.gitignore']

        with tempfile.NamedTemporaryFile('wb', delete=False) as tmp:
            zipfile = tmp.name
            project.repository_archive(format='zip', streamed=True, action=tmp.write)    

        with ZipFile(zipfile, 'r') as archive:
            members = list(filter(lambda x: x not in exclude, archive.namelist()))
            module_name = os.path.basename(os.path.dirname(members[0]))
            archive.extractall('./', members)                

        os.rename(module_name, name)
        manifest = os.path.join(os.getcwd(), name, "__manifest__.py")
        assert os.path.isfile(manifest), "Manifest doesn't found !"

        # with open(manifest, 'wb') as f:
        #     content = f.read()


    def get_project_path(self, name):
        workdir_path = self.config.get_var('local.workdir')
        project_path = os.path.join(workdir_path, name)
        
        return project_path

    def get_repo_path(self, project_name):
        return os.path.join(self.get_project_path(project_name), 'repositories')        

    def init_project(self, name):
        project_path = self.get_project_path(name)
        repo_path = self.get_repo_path(name)

        if not os.path.exists(project_path):
            os.makedirs(project_path)

        if not os.path.exists(repo_path):
            os.makedirs(repo_path)


    def prepare_compose_vals(self, database, requirements):
        requirements += ["inotify", "pdfminer.six"]
        output = set()

        for r in requirements:
            try:
                r = r.split("==")[0]
            except:
                pass

            if r not in output:
                output.add(r)
            
        requirements = "\n".join(list(output))
        _logger.info(requirements)

        vals = cfg.COMPOSE_TEMPLATE_VALS.copy()
        vals['services']['odoo']['image'] = "apik/odoo-saas:{}".format(database.odoo_version_id.name)
        vals['services']['odoo']['environment']['CUSTOM_REQUIREMENTS'] = requirements

        return vals
        

    def generate_compose_file(self, project_name, values):
        project_path = self.get_project_path(project_name)
        project = self.get_gitlab_project(self.config.get_var('scaffold.docker-template'))
        f = project.files.get(file_path=cfg.COMPOSE_TEMPLATE_FILE, ref='master')

        compose = Commpose()
        compose.from_content(f.decode())
        compose.update(values)
        compose.save(project_path)        


    def get_repositories(self, database):
        repositories = list()

        for repo in database.repos:
            base_url = repo.name.url
            odoo_version = database.odoo_version_group_id.major_version
            repository = repo.name.name

            branch = odoo_version if repo.name.version.name == "Standard" else "master"
            if repo.branche:
                branch += "-{}".format(repo.branche.name)
                
            if repo.name.identification.name == "Aucune":
                url = base_url
            else:
                user = repo.name.identification.identifiant
                password = repo.name.identification.password
                url = "{}://{}:{}@{}".format(base_url.split(':')[0],user,password,base_url.split(':')[1][2:])	
            
            vals = {
                'name': repository,
                'branch': branch,
                'url': url
            }
            repositories.append(vals)
            _logger.info(vals)
        
        return repositories


    def clone_repository(self, project_name, name, url, branch):
        repo_path = os.path.join(self.get_project_path(project_name), 'repositories')
        repository = GitRepository(name, url=url, branch=branch, path=repo_path)
        repository.clone()


    def get_odoo_instance(self, name):
        return "{}_odoo_1".format(name)


    def _exec_cmd(self, action, ctx):

        cmd_name = "_cmd_{}".format(action)
        cmd, args, options = self._get_default_cmd(action)
        custom_command = getattr(self, cmd_name, False)

        # run custom command if exists
        if custom_command:
            cmd, args, options = custom_command(cmd, args, options, **ctx)

        options.update({'_cwd': ctx['project_path']})

        _logger.info("Action {} on project {}\n\tOptions: {}.".format(action, ctx['project_name'], dict_to_string(options)))
        
        cmd(*args, **options)


    # default cmd, e.g. start / clear / ps
    def _get_default_cmd(self, name):
        values = cfg.COMMANDS.get(name)
        if not values:
            raise NotImplemented('Command {} not implemented.'.format(name))

        return values['cmd'], values.get('args', []), values.get('params', {})


    def _cmd_stop(self, cmd, args, options, **ctx):
        """Custom stop command"""
        if ctx.get('clear'):
            args.append('-v')

        return cmd, args, options


    def _cmd_logs(self, cmd, args, options, **ctx):
        """Custom logs command"""
        args.append(self.get_odoo_instance(ctx['project_name']))

        return cmd, args, options


    def _cmd_bash(self, cmd, args, options, **ctx):
        """Custom bash command"""
        args.insert(2, self.get_odoo_instance(ctx['project_name']))

        return cmd, args, options


    def _cmd_shell(self, cmd, args, options, **ctx):
        """Custom bash command"""
        args.insert(2, self.get_odoo_instance(ctx['project_name']))
        args.append('"odoo shell -d {} --no-http"'.format(ctx['project_name']))

        return cmd, args, options


    def _cmd_odoo_update(self, cmd, args, options, **ctx):
        """Custom bash command"""
        args.insert(2, self.get_odoo_instance(ctx['project_name']))
        args.append('"odoo -d {o[project_name]} -u {o[module]} --stop-after-init --no-http"'.format(o=ctx))

        return cmd, args, options


    def _cmd_cloc(self, cmd, args, options, **ctx):
        """Custom cloc command"""
        repo_path = self.get_repo_path(ctx['project_name'])
        extra_path = options.get('path', False)
        if extra_path:
            args = [extra_path] if os.path.exists(extra_path) else [os.path.join(repo_path, extra_path)]
        else:
            args = [repo_path]        

        return cmd, args, options


    def project_cmd(self, name, action, **kwargs):
        """Run command for project"""
        if not name in self.get_local_projects():
            raise ValueError('Project not found')

        
        ctx = {
            'project_name': name,
            'project_path': self.get_project_path(name)
        }
        ctx.update({k:kwargs.get(k, False) for k in ['clear', 'path', 'module']})

        return self._exec_cmd(action, ctx)
        

    def get_requirements(self, project_name):
        if not self.check_project(project_name):
            raise ValueError('Project...')

        repo_path = self.get_repo_path(project_name)

        requirements = []
        for r,d,f in os.walk(repo_path):
            for file in f:
                if file == 'requirements.txt':
                    with open(os.path.join(r, file), 'r') as tmp:
                        requirements += tmp.readlines()
        
        requirements = list(set([e.rstrip() for e in requirements])) 

        return requirements

    
apix = Apix()