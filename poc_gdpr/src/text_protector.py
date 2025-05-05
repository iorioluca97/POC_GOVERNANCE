from presidio_analyzer import AnalyzerEngine, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import OperatorConfig

from poc_gdpr.config.cfg import create_languages_config, download_spacy_model, LANGUAGE_CONFIG_PATH, DEFAULT_LANGUAGE
from poc_gdpr.config.logger import logger

from transformers import pipeline


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
    
    def anonymize_text_with_entities(self, text):        
        results = self.analyzer.analyze(text=text, language=self.language)
        # Anonymize the previously detected entities
        return self.anonymizer.anonymize(text=text, analyzer_results=results)
        

    def anonymize_text(self, 
        text,
        encryption_key="a1b2c3d4e5f6g7h8",  # 16-character key
        operator="encrypt",):

        results = self.analyzer.analyze(text=text, language=self.language)

        return self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
            "DEFAULT": OperatorConfig(operator, {"key": encryption_key}),
            }
        )

    def deanonymize_text(self, text, entities, encryption_key="a1b2c3d4e5f6g7h8", operator="decrypt"):
        # De-anonymize the text using the same key and operator
        return self.deanonymizer.deanonymize(
            text=text, # from anonymized_result.text,
            entities=entities, # from anonymized_result.items,
            operators={
                "DEFAULT": OperatorConfig(operator, {"key": encryption_key}),
            }
        )



class HFTransformersRecognizer(EntityRecognizer):
    def __init__(
        self,
        model_id_or_path=None,
        aggregation_strategy="simple",
        supported_language=DEFAULT_LANGUAGE,
        ignore_labels=["O", "MISC"],
    ):
        # inits transformers pipeline for given mode or path
        self.pipeline = pipeline(
            "token-classification", model=model_id_or_path, aggregation_strategy=aggregation_strategy, ignore_labels=ignore_labels
        )

        # Complete mapping for numeric labels and traditional NER labels
        self.label2presidio = {
            # Traditional NER labels
            "PER": "PERSON",
            "LOC": "LOCATION",
            "ORG": "ORGANIZATION",
            "PERSON": "PERSON",
            "LOCATION": "LOCATION",
            "ORGANIZATION": "ORGANIZATION",

            # Numeric labels - adjust these to match your model's output
            "LABEL_0": "PERSON",
            "LABEL_1": "LOCATION",
            "LABEL_2": "ORGANIZATION",
            "LABEL_3": "DATE_TIME",
            "LABEL_4": "EMAIL_ADDRESS",
            "LABEL_5": "PHONE_NUMBER",
            "LABEL_6": "CREDIT_CARD",
            "LABEL_7": "IBAN_CODE",
            "LABEL_8": "IP_ADDRESS",
        }

        # passes entities from model into parent class
        super().__init__(supported_entities=list(self.label2presidio.values()), supported_language=supported_language)



# if __name__ == "__main__":
#     text = """
#     Ciao, mi chiamo Mario Rossi e vivo a Roma. Il mio numero di telefono è 1234567890 e la mia email è
#     mariorossi@gmail.com, mentre il mio codice fiscale è RSSMRA85M01H501Z.
#     Ho un appuntamento il 15 marzo 2023 alle 14:30 presso l'ufficio di Milano.

#     Il mio numero di previdenza sociale è 987654321 e il mio numero di patente è ABC1234567.
#     """

#     text_protector = TextProtector(language="it")


#     logger.info("Analyzing text...")

    
#     results = text_protector.analyze_text(text)
#     logger.info(results)
    #         # Print detected entities
    # for result in results:
    #     print(f"Entity: {result.entity_type}, Text: {text[result.start:result.end]}, Score: {result.score}")

    # anonymized_result = text_protector.anonymize_text(text)
    # print("ANONYMIZED: ", anonymized_result.text)
    # # print("ANONYMIZED ENTITIES: ", anonymized_result.items)
    # de_anonymized_result = text_protector.deanonymize_text(
    #     text=anonymized_result.text,
    #     entities=anonymized_result.items
    # )
    # print("DE-ANONYMIZED: ", de_anonymized_result.text)
    # print("DE-ANONYMIZED ENTITIES: ", de_anonymized_result.items)
    # print("ANONYMIZED ENTITIES: ", anonymized_result.items)


    ##########################################################
    # italian_model = "dbmdz/bert-base-italian-xxl-cased"  # or another Italian language model
    # transformers_recognizer = HFTransformersRecognizer(italian_model, supported_language="it")
    # text_protector.analyzer.registry.add_recognizer(transformers_recognizer)

    # results = text_protector.analyzer.analyze(
    # text=text,
    # entities=["PERSON", "LOCATION", "ORGANIZATION", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "IT_FISCAL_CODE"],
    # language="it"
    # )

    # print(results)
