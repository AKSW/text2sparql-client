"""order matter scripts"""

import statistics


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


def combine_metrics(results: dict, new_metric: str) -> None:
    """Create a new average value that combines set_F with order_metric"""
    combined_list = []
    for value in results.values():
        if new_metric in value:
            combined_list.append(value[new_metric])
        else:
            combined_list.append(value["set_F"])
    results["average"][f"set_F_{new_metric}"] = statistics.fmean(combined_list)
