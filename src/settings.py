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
