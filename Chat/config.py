import os

user_db = 'contacts.pickle'
folder = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(folder, user_db)
