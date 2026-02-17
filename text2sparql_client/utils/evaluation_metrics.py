"""evaluation functions and classes"""

import statistics

import pytrec_eval


def filter_answer_dict(answer_dict: dict, order_required: list) -> dict:
    """Filter the questions where order is required for full evaluation"""
    return_dict = {}
    for question_id in order_required:
        return_dict[question_id] = answer_dict[question_id]
    return return_dict


def non_destructive_update(results: dict, new_results: dict, new_metric: str) -> None:
    """Update the results with order_metric where necessary without touching other metrics"""
    for key in new_results:
        results[key][new_metric] = new_results[key][new_metric]


def combine_averages(
    results: dict, new_metric: str, average_field: str = "average", old_metric: str = "set_F"
) -> None:
    """Create a new average value that combines set_F with order_metric"""
    combined_list = []
    for value in results.values():
        if new_metric in value:
            combined_list.append(value[new_metric])
        else:
            combined_list.append(value[old_metric])

    results[average_field][f"{old_metric}_{new_metric}"] = statistics.fmean(combined_list)


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
    ) -> dict:
        """Evaluate the model considering a true dictionary and a predicted dictionary.

        Args:
            predicted_dict (dict): Dictionary of the predicted lists
            ground_truth_dict (dict): Dictionary of the ground truth lists

        Returns:
           dict[dict[float]]: A dictionary with the average precision, recall and F1

        """
        results = {}
        for question_id_key in predicted_dict:  # noqa: PLC0206
            ground_truth = {question_id_key: ground_truth_dict[question_id_key]}
            prediction = {question_id_key: predicted_dict[question_id_key]}

            evaluator = pytrec_eval.RelevanceEvaluator(ground_truth, self.metrics)
            results_question = evaluator.evaluate(prediction)
            results.update(results_question)

        d: dict[str, float] = {}
        for measure in self.metrics:
            d[measure] = float(
                pytrec_eval.compute_aggregated_measure(
                    measure, [query_measures[measure] for query_measures in results.values()]
                )
            )
        results["average"] = d

        return results
