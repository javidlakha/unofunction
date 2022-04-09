import logging
import os
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)

LIBREOFFICE_PATH = os.environ['LIBREOFFICE_PATH']


class ConversionError(Exception):
    pass


def convert_file(
    filepath: str,
    outdir: str,
    convert_to: str,
    num_attempts: int,
) -> None:
    """
    Calls LibreOffice to convert `filepath` to the output type specified in 
    `convert_to`

    :param filepath: the path to the input file
    :param outdir: the path to the output directory
    :param convert_to: the file format of the converted type
    :param num_attempts: number of conversion attempts to make
    :raise ConversionError: if the conversion cannot be performed
    """
    commands = [
        LIBREOFFICE_PATH,

        # Without this, LibreOffice will return 'Fatal Error: The application
        # cannot be started. User installation could not be completed' because
        # AWS Lambda invocations do not have write access to
        # ~/.config/libreoffice
        '-env:UserInstallation=file:///tmp/'

        '--headless',
        '--invisible',
        '--nodefault',
        '--nofirststartwizard',
        '--nolockcheck',
        '--nologo',
        '--norestore',
        '--writer',

        '--convert-to',
        convert_to,

        '--outdir',
        outdir,

        filepath
    ]

    filepath_root, _ = os.path.splitext(filepath)
    expected_outpath = f'{filepath_root}.{convert_to}'

    # On a cold start, LibreOffice often requires several attempts to convert
    # a file before it succeeds
    for attempt in range(num_attempts):
        response = subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout = response.stdout.decode('utf8').strip()
        stderr = response.stderr.decode('utf8').strip()

        if response.returncode == 0 and os.path.exists(expected_outpath):
            logger.info(
                'Conversion successful on attempt '
                f'{attempt+1}/{num_attempts}. '
                f'stdout: "{stdout}". stderr: "{stderr}".'
            )
            break

        logger.info(
            f'Conversion attempt {attempt+1}/{num_attempts} failed. '
            f'stdout: "{stdout}". stderr: "{stderr}".'
        )

    # If all attempts fail, raise an error and report the output and error
    # messages from the last attempt
    else:
        raise ConversionError(
            'Unable to convert file. On the last attempt '
            f'({attempt+1}/{num_attempts}) the output was as follows - '
            f'stdout: "{stdout}". stderr: "{stderr}".'
        )
