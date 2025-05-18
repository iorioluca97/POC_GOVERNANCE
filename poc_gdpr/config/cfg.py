import yaml
from poc_gdpr.config.logger import logger
from presidio_anonymizer.entities import OperatorConfig

LANGUAGE_CONFIG_PATH : str = 'poc_gdpr/config/languages-config.yml'
DEFAULT_LANGUAGE : str = 'it'  # Default language is Italian
ENCRYPTION_KEY = "a1b2c3d4e5f6g7h8"  # Example encryption key
ENCRYPT_OPERATOR = {
    "DEFAULT": OperatorConfig("encrypt", {"key": ENCRYPTION_KEY}),
}
DECRYPT_OPERATOR = {
    "DEFAULT": OperatorConfig("decrypt", {"key": ENCRYPTION_KEY}),
}
def create_languages_config():
    """
    Create a configuration for Presidio NER engine with Spacy Italian model.
        """
    config = {
        'nlp_engine_name': 'spacy',
        'models': [
            {
                'lang_code': 'it',
                'model_name': 'it_core_news_sm'
            }
        ],
        'ner_model_configuration': {
            'model_to_presidio_entity_mapping': {
                'PER': 'PERSON',
                'LOC': 'LOCATION',
                'GPE': 'LOCATION',
                'ORG': 'ORGANIZATION',
                'DATE': 'DATE_TIME',
                'TIME': 'DATE_TIME',
                # 'MISC': 'MISCELLANEOUS'

            },
            'labels_to_ignore': [
                'CARDINAL',
                'EVENT',
                'LANGUAGE',
                'LAW',
                'MONEY',
                'ORDINAL',
                'PERCENT',
                'PRODUCT',
                'QUANTITY',
                'WORK_OF_ART'
            ],
            'low_confidence_score_multiplier': 0.4,
            'low_score_entity_names': [
                'ID',
                'ORG',
            ]
        }
    }
    #Check if the file already exists
    try:
        with open(LANGUAGE_CONFIG_PATH, 'r') as file:
            existing_config = yaml.safe_load(file)
            if existing_config == config:
                logger.info("languages-config.yml already exists and is up to date.")
                return
    except FileNotFoundError:
        logger.warning("languages-config.yml not found. Creating a new one.")
    # Write the configuration to a YAML file
    with open(LANGUAGE_CONFIG_PATH, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    logger.info("Successfully created languages-config.yml with the updated configuration")

def download_spacy_model():
    """
    Download the Italian spaCy model if not already downloaded.
    """
    try:
        import spacy
        try:
            spacy.load("it_core_news_sm")
            logger.info("Italian spaCy model is already downloaded.")
        except OSError:
            logger.warning("Italian spaCy model not found. Downloading...")
            spacy.cli.download("it_core_news_sm")
            logger.info("Italian spaCy model downloaded successfully.")
    except ImportError:
        import subprocess

        logger.warning("spaCy is not installed. Installing spaCy...")
        subprocess.run(["pip", "install", "spacy"], check=True)
        logger.warning("Downloading the Italian spaCy model...")
        subprocess.run(["python", "-m", "spacy", "download", "it_core_news_sm"], check=True)
        logger.warning("Italian spaCy model downloaded successfully.")
