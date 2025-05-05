import yaml
from poc_gdpr.config.logger import logger

LANGUAGE_CONFIG_PATH : str = 'poc_gdpr/config/languages-config.yml'
DEFAULT_LANGUAGE : str = 'it'  # Default language is Italian

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

    # Write the configuration to a YAML file
    with open(LANGUAGE_CONFIG_PATH, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print("Successfully created languages-config.yml with the updated configuration")

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
