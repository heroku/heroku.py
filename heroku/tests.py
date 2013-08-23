import os
import heroku
from pprint import pprint# noqa

HEROKU_API_KEY = os.environ.get('HEROKU_API_KEY', False)
TEST_EMAIL = os.environ.get('TEST_EMAIL', False)

heroku_conn = heroku.from_key(HEROKU_API_KEY)
#newapp = heroku_conn.create_app(name='testing125146513', stack='bamboo', region_name='us')
#collab = newapp.add_collaborator(email=TEST_EMAIL, silent=1)
#print newapp.collaborators()
#config = newapp.config()
#config['TEST2'] = None
#print newapp.domains()

#domain2 = newapp.add_domain('testyzz2.testing.com')
#print newapp.domains()
#newapp.remove_domain('testyzz2.testing.com')
#domain.remove()
#print newapp.domains()

app = heroku_conn.app('sharehoodfrontend')
#app.enable_feature('user-env-compile')
#app.disable_feature('user-env-compile')
#print app.labs()
#print heroku_conn.features()
#domain = app.add_domain('testyzz1.testing.com')
#domain = app.add_domain('testyzz2.testing.com')
#domain = app.add_domain('testyzz3.testing.com')
#domain = app.add_domain('testyzz4.testing.com')
#domain = app.add_domain('testyzz5.testing.com')
#domain = app.add_domain('testyzz6.testing.com')
#domain = app.add_domain('testyzz7.testing.com')

#iterator = app.stream_log(lines=1)
#for line in iterator:

    # filter out keep-alive new lines
    #if line:
        #print "{0}".format(line)

logs = app.get_log(lines=100)
print logs

#print app.domains(limit=1)
#print app.domains(valrange='domain ]martinsharehoodadmin.herokuapp.com..; max=1')
#dyno = app.run_command_detached('fab celery.shutdown_process', printout=True)
#dyno = app.run_command_detached('fab -l', printout=True)
#pprint(dyno)
#dyno.remove()
#formations = app.process_formation(limit=1)
#for formation in formations:
    #formation.scale(0)
    #print app._h._last_request_id
    #formation.restart()

#for dyno in app.dynos():
    #dyno.restart()
    #dyno.scale(1)

#pprint(app.releases(limit=10))
#app.restart()
#del config['TEST2']

#newapp.remove_collaborator('testing125146513@gmail.com')
#collab.remove()
#pprint(newapp.addons)
#app = heroku_conn.app('testing125146513')
#for addon in app.addons:
    #print addon.app.name, " - ", addon.plan.name

#app = heroku_conn.app('testing125146513')
#for addon in app.addons:
    #print addon.app.name, " - ", addon.plan.name

#addons = heroku_conn.addon_services()
#pprint(addons)

#pg_addon = heroku_conn.addon_services('6235c964-8b3c-47e0-952f-8d8f6a2d53f5')
#pg_addon = heroku_conn.addon_services(id_or_name='heroku-postgresql')
#pprint(pg_addon)

#app.install_addon(plan_name='heroku-postgresql:dev')
#print "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"

#for addon in app.addons:
    #print addon.app.name, " - ", addon.plan.name, " - ", addon.id
    #pprint(addon.app)
    #addon.upgrade(name='heroku-postgresql:basic')
    #addon.delete()

#app.delete()

print heroku_conn._last_request_id
assert(False)
