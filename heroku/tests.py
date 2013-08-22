import os
import heroku
from pprint import pprint# noqa

HEROKU_API_KEY = os.environ.get('HEROKU_API_KEY', False)
TEST_EMAIL = os.environ.get('TEST_EMAIL', False)

heroku_conn = heroku.from_key(HEROKU_API_KEY)
#newapp = heroku_conn.create_app(name='testing125146513', stack='cedar', region_name='us')
#collab = newapp.add_collaborator(email=TEST_EMAIL, silent=1)
#print newapp.collaborators()
#config = newapp.config()
#config['TEST2'] = None
#print newapp.domains()

#domain = newapp.add_domain('testyzz1.testing.com')
#domain2 = newapp.add_domain('testyzz2.testing.com')
#print newapp.domains()
#newapp.remove_domain('testyzz2.testing.com')
#domain.remove()
#print newapp.domains()

app = heroku_conn.app('testing125146513')
#dyno = app.run_command_detached('fab celery.shutdown_process', printout=True)
#dyno = app.run_command_detached('fab -l', printout=True)
#pprint(dyno)
#dyno.remove()
#formations = app.process_formation()
#for formation in formations:
    #formation.scale(1)
    #formation.restart()

#for dyno in app.dynos():
    #dyno.restart()
    #dyno.scale(1)

pprint(app.releases)
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

assert(False)
