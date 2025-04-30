"""evaluation classes"""

import typing

import pytrec_eval


class DBpediaDict2PytrecDict:
    """Transform the DBpedia returned dict into a dict readable to compute the metrics"""

    def __init__(self, question: str) -> None:
        """Initialize the DBpediaDict2PytrecDict class.

        Args:
            question (str): The question that generate the sparql query.

        """
        self.question = question

    def tranform(self, sparql_dict: dict) -> dict:
        """Transform a sparql dict into a dict to be evaluated through the pytrec library.

        Args:
            sparql_dict (dict): Dictionary of the URIs, returned by the end-point

        Returns:
           dict: Dictionary of the predicted lists in which all items have the same weight

        """
        d: dict = {}
        if "boolean" in sparql_dict:
            bool_result = sparql_dict["boolean"]
            d[self.question] = {}
            d[self.question]["true"] = 1 if bool_result else 0
        else:
            list_results = sparql_dict["results"]["bindings"]
            list_vars = sparql_dict["head"]["vars"]
            d[self.question] = {}
            for var in list_vars:
                for value in list_results:
                    if var in value:
                        d[self.question][value[var]["value"]] = 1
        return d


class Evaluation:
    """Computes the F1, Recall and Precision for two list considering the Pytrec_eval library.

    need: pip install pytrec_eval numpy scipy
    """

    def __init__(self, model_name: str, metrics: set[str] | None = None) -> None:
        """Initialize the Evaluation class.

        Args:
            model_name (str): The name of the model that generates the predicted_dicts
            metrics (dict): Name of the evaluated metrics. See pytrec_eval.supported_measures

        """
        if metrics is None:
            metrics = {"set_F", "set_P", "set_recall"}
        self.model_name = model_name
        self.metrics = metrics

    def evaluate(
        self,
        predicted_dict: dict[str, dict[str, int]],
        ground_truth_dict: dict[str, dict[str, int]],
    ) -> dict | typing.Any:  # noqa: ANN401
        """Evaluate the model considering a true dictionary and a predicted dictionary.

        Args:
            predicted_dict (dict): Dictionary of the predicted lists
            ground_truth_dict (dict): Dictionary of the ground truth lists

        Returns:
           dict[dict[float]]: A dictionary with the average precision, recall and F1

        """
        evaluator = pytrec_eval.RelevanceEvaluator(ground_truth_dict, self.metrics)
        results = evaluator.evaluate(predicted_dict)
        d: dict[str, float] = {}
        for measure in self.metrics:
            d[measure] = float(
                pytrec_eval.compute_aggregated_measure(
                    measure, [query_measures[measure] for query_measures in results.values()]
                )
            )
        results["average"] = d

        return results
