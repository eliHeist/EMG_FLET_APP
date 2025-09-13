import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# reading .env file
environ.Env.read_env()


DEBUG = env('DEBUG')
DATA_ENDPOINT = env('DATA_ENDPOINT')
LOW_THRESHOLD = 2000
HIGH_THRESHOLD = 3275
TICKS_ON_GRAPH = 100
UPDATE_FREQUENCY = 500

def toggleDebug():
    global DEBUG
    DEBUG = not DEBUG
