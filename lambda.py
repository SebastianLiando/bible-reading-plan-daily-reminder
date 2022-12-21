from send_reading import main as run_send_reading
from fetch_schedule import main as run_fetch_schedule


def lambda_handler(event: dict, context):  # NOSONAR
    task = event.get('task')

    if task == 'SEND_READING':
        print('Running SEND_READING task.')
        run_send_reading()
    elif task == 'UPDATE_SCHEDULE':
        print('Running UPDATE_SCHEDULE task.')
        run_fetch_schedule()
    else:
        raise ValueError(
            f'No task named {task}! Please check your LAMBDA_TASK environment variable configuration.')
