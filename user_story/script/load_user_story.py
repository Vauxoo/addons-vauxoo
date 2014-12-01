import xmlrpclib
import logging
import time
_logger = logging.getLogger(__name__)

# Source server info
HOST = 'vauxoo.info'
PORT = 18869
DB = 'herrera'
USER = 'admin'
PASS = 'admin'
URL = 'http://%s:%d/xmlrpc/' % (HOST, PORT)
COMMON_PROXY = xmlrpclib.ServerProxy(URL + 'common')
OBJECT_PROXY = xmlrpclib.ServerProxy(URL + 'object')

uid = COMMON_PROXY.login(DB, USER, PASS)

# Destiny server info
HOST2 = 'localhost'
PORT2 = 8069
DB2 = 'migration3'
USER2 = 'admin'
PASS2 = '12345'
URL2 = 'http://%s:%d/xmlrpc/' % (HOST2, PORT2)
COMMON_PROXY2 = xmlrpclib.ServerProxy(URL2 + 'common')
OBJECT_PROXY2 = xmlrpclib.ServerProxy(URL2 + 'object')

UID2 = COMMON_PROXY2.login(DB2, USER2, PASS2)


def search_in_destiny(model, name):
    return OBJECT_PROXY2.execute(DB2, UID2, PASS2, model, 'search',
                                 [("name", "ilike", name)])


def create_in_destiny(model, model_dict=None):
    if model_dict is None:
        model_dict = {}
    if model_dict:
        return OBJECT_PROXY2.execute(DB2, UID2, PASS2, model, 'create',
                                     model_dict)
    else:
        _logger.warning('dictionary empty, model: %d', model)
        return False


def read_in_source(model, model_id, fields=None):
    if fields is None:
        fields = []
    return OBJECT_PROXY.execute(DB, uid, PASS, model, 'read',
                                [model_id], fields)[0]


def read_in_destiny(model, model_id, fields=None):
    if fields is None:
        fields = []
    return OBJECT_PROXY2.execute(DB2, UID2, PASS2, model, 'read', [model_id],
                                 fields)[0]


def user_matching(user_id):
    # Capturamos el diccionario de usuario con los valores del origen
    user = read_in_source(
        'res.users', user_id,
        ['name', 'groups_id', 'login', 'password', 'email',
         'signature', 'notification_email_send', 'company_id'])

    # Si no existe el usuario en el destino
    if not search_in_destiny('res.users', user.get('name')):

        # Inicilizamos algunos campos necesario
        groups_id = []

        # Ubicamos los grupos de permiso en el destino
        for group_n in user.get('groups_id', []):
            group_name = read_in_source(
                'res.groups', group_n, ['name']).get('name')
            if search_in_destiny('res.groups', group_name):
                groups_id.append(search_in_destiny(
                    'res.groups', group_name)[0])

        # Actualizamos el diccionario de usuario con la lista de grupos de
        # permisos
        user.update({'groups_id': [(6, 0, groups_id)]})

        # Ubicamos los datos de res.company en el destino, sino existe se crea
        company_id = user.get('company_id', []) and search_in_destiny(
            'res.company', user.get('company_id', [])[1])
        company_id = company_id and company_id[0] or create_in_destiny(
            'res.company', {'name': user.get('company_id', [])[1]})

        # Actualizamos company_id en el diccionario de usuario
        user.update({'company_id': company_id})

        # Extraemos id del diccionario para que no ocurra error
        user.pop('id')
        user.pop('groups_id')

        # Almacenamos el usuario en el destino
        user_id = create_in_destiny('res.users', user)

    # Si existe el usuario en el destino
    else:
        user_id = search_in_destiny('res.users', user.get('name'))[0]

    return user_id


def __main__():

    _logger.info('ha comenzado la carga de datos')
    begin_p = time.time()

    user_story_ids = OBJECT_PROXY.execute(
        DB, uid, PASS, 'user.story', 'search', [])
    user_story_dict = OBJECT_PROXY.execute(
        DB, uid, PASS, 'user.story', 'read', user_story_ids, [])

    for user_story in user_story_dict:
        accep_crit_ids = user_story.get('accep_crit_ids')
        user_id = user_story.get('user_id')[0]
        user_story_name = user_story.get('name')

        _logger.info('Evaluando la historia %s', user_story_name)

        # Si no existe la historia de usuario (user_story)
        if not search_in_destiny('user.story', user_story_name):
            _logger.info('Creando la historia %s', user_story_name)
            begin = time.time()

        # Comprobamos si tiene elementos accep_crit_ids, de ser asi creamos
        # estos elementos en el destino
            if accep_crit_ids:
                accep_crit_dict = OBJECT_PROXY.execute(
                    DB, uid, PASS, 'acceptability.criteria', 'read',
                    accep_crit_ids, ['name', 'scenario'])
                accep_crit_o2m = []
                for crit_dic in accep_crit_dict:
                    accep_crit_o2m.append((0, 0, crit_dic))

        # Ubicamos los datos de project.project en el destino, sino existe se
        # crea
            project = read_in_source(
                'project.project', user_story.get('project_id', [])[0],
                ['name', 'state', 'date_start', 'date_end',
                 'privacy_visibility', 'priority', 'user_task',
                 'user_id', 'members'])

        # Inicilizamos la lista de los miembros del proyecto
            project_members = []

        # Por cada miembro del origen hacemos el match user en el destino
            for project_member in project.get('members', []):
                project_members.append(user_matching(project_member))

        # Actualizamos el diccionario de project con la lista miembros
            project.update({'members': [(6, 0, project_members)]})

        # Extraemos id del diccionario para que no ocurra error
            project.pop('id')

        # Actualizamos el project manager en el diccionario de project del
        # destino
            project.update({'user_id': user_matching(
                project.get('user_id')[0])})

        # Ubicamos los datos de project en el destino, sino existe se crea
            project_id = user_story.get('project_id', []) \
                and search_in_destiny('project.project',
                                      project.get('name', []))
            project_id = project_id and project_id[
                0] or create_in_destiny('project.project', project)

        # Actualizamos el diccionario de user_story
            user_story.pop('id')
            user_story.update(
                {"accep_crit_ids": accep_crit_ids and accep_crit_o2m,
                 "user_id": user_matching(user_id),
                 "task_ids": [],
                 "project_id": project_id})

        # Almacenamos el user_story en el destino
            create_in_destiny('user.story', user_story)
            end = time.time()
            _logger.info('Creada la historia %s en %ss',
                         user_story_name, end - begin)

        else:
            _logger.info('Ya existe la historia %s', user_story_name)

    end_p = time.time()
    _logger.info('Creadas todas las historias en %ss', end_p - begin_p)
    _logger.info('ha finalizado la carga de datos')

__main__()
