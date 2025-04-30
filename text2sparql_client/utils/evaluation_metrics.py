"""evaluation classes"""

import pytrec_eval
from typing import Dict

class DBpediaDict2PytrecDict:
    """Transform the DBpedia returned dict into a dict readable to compute the metrics
    """

    def __init__(self, question: str) -> None:
        """Initializes the DBpediaDict2PytrecDict class.
        Args:
            question (str): The question that generate the sparql query.
        """
        self.question = question
    
    def tranform(self, dbpedia_dict: dict)-> Dict:
        """Transform the dbpedia returned dict into a dict to be evaluated through the pytrec library.
        
        Args:
            dbpedia_dict (dict): Dictionary of the predicted URIs, returned by the dbpedia end-point of HTWK

        Returns:
           Dict[Dict[str]]: Dictionary of the predicted lists in which all items have the same weight
        """
        d = {}  # d: dict[dict[str]]
        if 'boolean' in dbpedia_dict:
            bool_result = dbpedia_dict['boolean']
            d[self.question] = {}
            d[self.question]['true'] = 1 if bool_result else 0
        else:
            list_results = dbpedia_dict['results']['bindings']
            list_vars = dbpedia_dict['head']['vars']
            d[self.question] = {}
            for var in list_vars:
                for value in list_results:
                    if var in value:
                        d[self.question][value[var]['value']] = 1
        return d

class Evaluation:
    """Computes the F1, Recall and Precision for two list considering the Pytrec_eval library.
        need: pip install pytrec_eval numpy scipy
    """
    def __init__(self, model_name: str, metrics: str = {'set_F', 'set_P', 'set_recall'}) -> None:
        """Initializes the Evaluation class.
        
        Args:
            model_name (str): The name of the model that generates the predicted_dicts (Dbpedia lists)
            metrics (dict): Name of the evaluated metrics. See pytrec_eval.supported_measures
        """
        self.model_name = model_name
        self.metrics = metrics

    def evaluate(self, predicted_dict: dict, ground_truth_dict: dict)-> Dict[float]:
        """Evaluates the model considering a true dictionary and a predicted dictionary.
        
        Args:
            predicted_dict (dict): Dictionary of the predicted lists, all items must have the same weight
            ground_truth_dicts (dict): Dictionary of the ground truth lists, all items must have the same weight
        
        Returns:
           Dict[Dict[str]]: A dictionary with the average precision, recall and F1 for each predicted list.
        """
        evaluator = pytrec_eval.RelevanceEvaluator(ground_truth_dict, self.metrics)
        results = evaluator.evaluate(predicted_dict)
        d = {} # d: dict[dict[str]]
        for measure in self.metrics:
            d[measure] = float(pytrec_eval.compute_aggregated_measure(measure,[query_measures[measure] for query_measures in results.values()]))
        results['average'] = d

        return results