import json
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer.entities import OperatorConfig
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine, OperatorConfig
from presidio_anonymizer.operators import Operator, OperatorType
from pydantic import ValidationError

from poc_gdpr.config.cfg import (
    create_languages_config,
    download_spacy_model,
    LANGUAGE_CONFIG_PATH,
    DEFAULT_LANGUAGE,
    ENCRYPTION_KEY,
    ENCRYPT_OPERATOR,
    DECRYPT_OPERATOR,
)
from poc_gdpr.config.logger import logger
from typing import Dict




class TextProtector:
    def __init__(self, language=DEFAULT_LANGUAGE, conf_file=LANGUAGE_CONFIG_PATH):
        """
        Initialize the TextProtector with the specified language.
        :param language: Language code (default is Italian).
        """
        self.setup()

        self.language = language
        # Initialize the NLP engine provider and create an NLP engine
        self.provider = NlpEngineProvider(conf_file=conf_file)
        # Create the NLP engine using the configuration file
        self.nlp_engine = self.provider.create_engine()
        # Initialize the AnalyzerEngine with the specified language
        self.analyzer = AnalyzerEngine(nlp_engine=self.nlp_engine, supported_languages=[self.language])
        # Initialize the AnonymizerEngine and DeanonymizeEngine
        self.anonymizer = AnonymizerEngine()
        self.deanonymizer = DeanonymizeEngine()

    
    def setup(self):
        create_languages_config()
        download_spacy_model()

    def analyze_text(self, text):
        """
        Analyze the text for PII entities.
        :param text: The text to analyze.
        :return: List of detected entities.
        """
        # Analyze the text for PII entities
        results = self.analyzer.analyze(text=text, language=self.language)

        return results
    
    def anonymize_text_with_encryption(self, text, encryption_key=ENCRYPTION_KEY):
        # Anonymize the text with encryption
        return self.anonymizer.anonymize(
            text=text,
            operators={
                ENCRYPT_OPERATOR: OperatorConfig(ENCRYPT_OPERATOR, {"key": encryption_key}),
                DECRYPT_OPERATOR: OperatorConfig(DECRYPT_OPERATOR, {"key": encryption_key}),
            }
        )
    
    def deanonymize_text_with_encryption(self, text, encryption_key=ENCRYPTION_KEY):
        # De-anonymize the text with encryption
        return self.deanonymizer.deanonymize(
            text=text,
            operators={
                ENCRYPT_OPERATOR: OperatorConfig(ENCRYPT_OPERATOR, {"key": encryption_key}),
                DECRYPT_OPERATOR: OperatorConfig(DECRYPT_OPERATOR, {"key": encryption_key}),
            }
        )
    
class InstanceCounterAnonymizer(Operator):
    """
    Anonymizer which replaces the entity value
    with an instance counter per entity.
    """

    REPLACING_FORMAT = "<{entity_type}_{index}>"

    def operate(self, text: str, params: Dict = None) -> str:
        """Anonymize the input text."""

        entity_type: str = params["entity_type"]

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: Dict[Dict:str] = params["entity_mapping"]

        entity_mapping_for_type = entity_mapping.get(entity_type)
        if not entity_mapping_for_type:
            new_text = self.REPLACING_FORMAT.format(
                entity_type=entity_type, index=0
            )
            entity_mapping[entity_type] = {}

        else:
            if text in entity_mapping_for_type:
                return entity_mapping_for_type[text]

            previous_index = self._get_last_index(entity_mapping_for_type)
            new_text = self.REPLACING_FORMAT.format(
                entity_type=entity_type, index=previous_index + 1
            )

        entity_mapping[entity_type][text] = new_text
        return new_text

    @staticmethod
    def _get_last_index(entity_mapping_for_type: Dict) -> int:
        """Get the last index for a given entity type."""

        def get_index(value: str) -> int:
            return int(value.split("_")[-1][:-1])

        indices = [get_index(v) for v in entity_mapping_for_type.values()]
        return max(indices)

    def validate(self, params: Dict = None) -> None:
        """Validate operator parameters."""

        if "entity_mapping" not in params:
            raise ValueError("An input Dict called `entity_mapping` is required.")
        if "entity_type" not in params:
            raise ValueError("An entity_type param is required.")

    def operator_name(self) -> str:
        return "entity_counter"

    def operator_type(self) -> OperatorType:
        return OperatorType

class InstanceCounterDeanonymizer(Operator):
    """
    Deanonymizer which replaces the unique identifier 
    with the original text.
    """

    def operate(self, text: str, params: Dict = None) -> str:
        """Anonymize the input text."""

        entity_type: str = params["entity_type"]

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: Dict[Dict:str] = params["entity_mapping"]

        if entity_type not in entity_mapping:
            raise ValueError(f"Entity type {entity_type} not found in entity mapping!")
        if text not in entity_mapping[entity_type].values():
            raise ValueError(f"Text {text} not found in entity mapping for entity type {entity_type}!")

        return self._find_key_by_value(entity_mapping[entity_type], text)

    @staticmethod
    def _find_key_by_value(entity_mapping, value):
        for key, val in entity_mapping.items():
            if val == value:
                return key
        return None
    
    def validate(self, params: Dict = None) -> None:
        """Validate operator parameters."""

        if "entity_mapping" not in params:
            raise ValueError("An input Dict called `entity_mapping` is required.")
        if "entity_type" not in params:
            raise ValueError("An entity_type param is required.")

    def operator_name(self) -> str:
        return "entity_counter_deanonymizer"

    def operator_type(self) -> OperatorType:
        return OperatorType.Deanonymize

class JsonValidator():
    def __init__(self, 
        pydantic_model_not_validated=None,
        pydantic_model_validated=None,
        raw_json=None,
        entity_mapping=None,
        ):
        self.pydantic_model_not_validated = pydantic_model_not_validated
        self.pydantic_model_validated = pydantic_model_validated
        self.raw_json = self._clean(raw_json)
        self.entity_mapping = entity_mapping


    def _clean(self, raw_json):
        cleaned_json = raw_json.replace("```json", "").replace("```", "")
        return json.loads(cleaned_json)
    
    def validate(self,) -> dict:
        """
        Validate the text.
        :return: True if valid, False otherwise.
        """
        # First validation
        data = self._first_validation(self.raw_json)
        if not data:
            return {}

        # Second validation
        data = self._second_validation(data, self.entity_mapping)

        return data


    def _first_validation(self, data: dict) -> dict:
        """
        Validate the text.
        :param text: The text to validate.
        :return: True if valid, False otherwise.
        """
        try:
            data = self.pydantic_model_not_validated(**data)
            return data.__dict__
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {}
        
    def _second_validation(self, data: dict, entity_mapping: dict) -> dict:
        data_copy = data.copy()
        entity_mapping_copy = entity_mapping.copy()

        for entity_value  in entity_mapping_copy.values():
            for value, _type in entity_value.items():
                for key, val in data.items():
                    if val == _type:
                        data_copy[key] = value

        try:
            data = self.pydantic_model_validated(**data_copy)
            return data.__dict__
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {}
