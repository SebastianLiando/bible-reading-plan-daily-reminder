from config.env import LAMBDA_TASK, LambdaTask
from send_reading import main as run_send_reading
from fetch_schedule import main as run_fetch_schedule


def lambda_handler(event, context):  # NOSONAR
    print(event)

    if LAMBDA_TASK == LambdaTask.SEND_READING:
        print('Running SEND_READING task.')
        run_send_reading()
    elif LAMBDA_TASK == LambdaTask.UPDATE_SCHEDULE:
        print('Running UPDATE_SCHEDULE task.')
        run_fetch_schedule()
    else:
        raise ValueError(
            f'No task named {LAMBDA_TASK}! Please check your LAMBDA_TASK environment variable configuration.')
