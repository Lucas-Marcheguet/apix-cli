
import odoorpc
import configparser
import os
import sys
import requests
# import gitlab
# import time
# import shutil
import logging
import sh
import tempfile


from tqdm import tqdm

import apixdev.config as cfg
from apixdev.tools import dict_to_string
from apixdev.repository import GitRepository
from apixdev.common import SingletonMeta

_logger = logging.getLogger(__name__)




class Apix(metaclass=SingletonMeta):

    _odoo = None
    _config = None
    _path = ""

    def __init__(self):
        _logger.error("Hé ApiX init")
        self.load()
        self._output = ""


    @property
    def is_ready(self):
        return True if self._config and not len(self.get_missing_values()) else False


    @property
    def filepath(self):
        return os.path.join(os.environ['HOME'], cfg.CONFIG_PATH, cfg.CONFIG_FILE)


    def logout(self):
        values = self._config['apix']
        self._config['apix'] = {k:v for k,v in values.items() if k not in cfg.MANDATORY_VALUES}
        self.save()        


    def save(self):
        _logger.info('Save configuration to {}.'.format(self.filepath))
        with open(self.filepath, 'w') as configfile:
            self._config.write(configfile)        


    def _get_default_values(self):
        return {
            'port': cfg.DEFAULT_PORT,
            'protocol': cfg.DEFAULT_PROTOCOL, 
            'timeout': cfg.DEFAULT_TIMEOUT, 
            'default_password': cfg.DEFAULT_PASSWORD,  
        }

    
    def _prepare_config(self):
        return {
            'url': '', 
            'port': '', 
            'protocol': '', 
            'timeout': '', 
            'database': '',
            'user': '', 
            'password': '',  
        }


    def load(self):
        
        self._config = configparser.ConfigParser()
        path = os.path.join(os.environ['HOME'], cfg.CONFIG_PATH)

        if not os.path.isdir(path):
            os.makedirs(path)

        if not os.path.isfile(self.filepath):
            _logger.info("New configuration file.")
            vals = self._prepare_config()
            vals.update(self._get_default_values())

            self._config['apix'] = vals
            self.save()
        else:
            _logger.info("Load configuration from {}.".format(self.filepath))
            self._config.read(self.filepath)

    
    def set_vars(self, vals):
        values = self._config['apix']
        values.update(vals)
        self._config['apix'] = values

        self.save()


    def get_vars(self):
        vals = dict()
        sections = ['apix']

        for section in sections:
            vals.update({"{}.{}".format(section,k):v for k,v in self._config[section].items() if k not in cfg.IGNORED_VALUES})

        return vals


    def get_missing_values(self):

        vars = self._config['apix']
        missing_values = dict()
        
        for key in cfg.MANDATORY_VALUES:
            if not key in vars or not vars.get(key, False):
                missing_values[key] = ''
        
        return missing_values.items()


    @property
    def odoo(self):
        if not self._odoo:
            self._odoo = self._get_odoo()
        return self._odoo

        
    def _get_odoo(self):

        url = self._config.get('apix', 'url')
        params = {k:v for k,v in self._config['apix'].items() if k in ['port', 'protocol', 'timeout']}
        _logger.warning(params)

        obj = odoorpc.ODOO(url, **params)
        try:
            obj.login(
                self._config.get('apix', 'database'), 
                self._config.get('apix', 'user'),
                self._config.get('apix', 'password'))
        except odoorpc.error.RPCError as e:
            _logger.error(e)
            print(e)
            obj = None

        if obj is None:
            sys.exit(1)

        return obj


    def get_ticket(self, id):
        Ticket = self.odoo.env['helpdesk.ticket']
        Database = self.odoo.env['saas.database']
        ticket = Ticket.browse(id)


        database_type = 'Production' if ticket.statut_odoo == 'Production' else 'Recette'
        domain = [('partner_id', 'in', ticket.partner_instance.ids), ('database_type_id.name', '=', database_type)]
        database_id = Database.search(domain, limit=1)

        if not database_id:
            _logger.error('No database found.')
            sys.exit(1)

        database = Database.browse(database_id)
        branch_dev = '{}-dev-{}'.format(database.odoo_version_group_id.major_version, ticket.id)
        _logger.info(branch_dev)

        return ticket
        # statut_developpement


    def get_databases(self, name, exact=True):
        Database = self.odoo.env['saas.database']
        domain = [('name', '=', name)] if exact else [('name', 'ilike', name)]

        ids = Database.search(domain)
        databases = Database.browse(ids)

        return databases


    def get_repositories(self, database):
        repositories = list()

        for repo in tqdm(database.repos):
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
            
            repositories.append([repository, branch, url])
            _logger.info([repository, branch, url])
        
        return repositories
		     


    @property
    def workdir(self):
        return self._config.get('apix', 'workdir')


    def _check_project(self, name):
        content = os.listdir(os.path.join(self.workdir, name))

        if not 'docker-compose.yml' in content:
            return False
        
        if not 'repositories' in content:
            return False

        return True

    
    @property
    def projects(self):
        if not os.path.isdir(self.workdir):
            os.makedirs(self.workdir)

        projects = [dir for dir in os.listdir(self.workdir) if self._check_project(dir)]
        projects.sort()

        return projects


    def get_odoo_instance(self, name):
        return "{}_odoo_1".format(name)

    
    def _buffer(self, buffer):
        self._output += buffer

    def clear(self):
        self._output = ""

    @property
    def output(self):
        return self._output

    def project_cmd(self, name, action, **kwargs):
        if not name in self.projects:
            raise ValueError('Project not found')

        clear = kwargs.get('clear', False)

        if action == 'clear':
            clear = True

        project_path = os.path.join(self.workdir, name)
        params = dict(_cwd=project_path)
        cmd = None

        if action == 'run':
            args = ["up", "-d"]
            cmd = sh.docker_compose
        elif action == 'ps':
            # args = ["ps"]
            # cmd = sh.docker_compose
            # params.update(_tee='out', _out=sys.stdout)


            args = ['compose','ps', '--format', 'json']
            cmd = sh.docker
            params.update(_tee='out', _out=self._buffer)

        elif action in ['stop', 'clear']:
            args = ["down"]
            if clear:
                args.append("-v")
            cmd = sh.docker_compose
        elif action == 'logs':
            args = ['logs', '-f', self.get_odoo_instance(name)]
            params.update(_tee='out', _out=sys.stdout)
            cmd = sh.docker
        elif action == 'bash':
            args = ['exec', '-it', self.get_odoo_instance(name), 'bash'],
            params.update(_fg=True)
            cmd = sh.docker
        else:
            raise NotImplemented('Command {} not implemented.'.format(action))

        # docker ps --format "{{json .}}"

        _logger.info("Action {} on project {}.\n\tArguments: {}\n\tOptions: {}.".format(action, name, dict_to_string(kwargs), dict_to_string(params)))
        
        cmd(*args, **params)
        
        return True
        
        
        

    def new_project(self, name, database=None):

        if not database:
            database = self.get_databases(name)

        repositories = self.get_repositories(database)

        project_path = os.path.join(self.workdir, name)
        repo_path = os.path.join(project_path, 'repositories')

        if not os.path.isdir(repo_path):
            # raise ValueError("Project {} already exists !".format(name))
            os.makedirs(repo_path)

        for repo_name, branch, url in repositories:
            repo = GitRepository(repo_name, branch=branch, url=url, path=repo_path)
            repo.clone()



    

    def backup_and_restore(self, name, database, method='backup', path=None):

        odoo_url = database.main_hostname
        odoo_db = database.name
        odoo_admin_password = database.admin_password
        fp = None

        # Get backup
        if method == 'backup':
            print("Backup database...")
            data = {
                'master_pwd' : odoo_admin_password,
                'name': odoo_db,
                'backup_format': 'zip',
            }
            r = requests.post(cfg.BACKUP_URL.format(odoo_url), data=data)
            
            fp = tempfile.TemporaryFile()
            fp.write(r.content)

        elif method == 'file':
            fp = open(path, 'rb')

        elif method == 'download':
            raise NotImplemented('Download method not implemented.')
        else:
            raise ValueError("Unknown method '{}'".format(method))

        if not fp:
            raise ValueError('No backup file to restore.')

        print("Restore database...")
        # Restore
        data = {
            'master_pwd' : self._config.get('apix', 'default_password'),
            'name': odoo_db,
        }
        files = {
            'backup_file': fp
        }
        r = requests.post(cfg.RESTORE_URL.format(cfg.LOCAL_URL),data=data,files=files)
        print("Restauration terminée !")
        fp.close()


    