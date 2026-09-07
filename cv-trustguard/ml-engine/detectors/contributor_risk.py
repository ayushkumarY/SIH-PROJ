import json


RISK_WEIGHTS = {
    "exact_duplicate": 10,
    "near_duplicate": 15,
    "possible_label_anomaly": 25,
    "possible_ood": 30,
    "trigger_anomaly": 40
}


def load_contributors(metadata_path):

    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data.get("contributors", [])


def create_contributor_map(contributors):

    contributor_map = {}

    for item in contributors:

        image = item.get("image")

        contributor_map[image] = {
            "contributor": item.get(
                "contributor",
                "Unknown"
            ),
            "batch": item.get(
                "batch",
                "Unknown"
            ),
            "source": item.get(
                "source",
                "Unknown"
            )
        }

    return contributor_map


def find_original_image(image_name, contributor_map):

    # Direct match
    if image_name in contributor_map:
        return image_name

    # Trigger attack files:
    # trigger_car1.jpg -> car1.jpg
    if image_name.startswith("trigger_"):

        original_name = image_name[
            len("trigger_"):
        ]

        if original_name in contributor_map:
            return original_name

    # Other attack/generated files can be
    # mapped here in the future.

    return None


def get_risk_level(score):

    if score >= 70:
        return "CRITICAL"

    elif score >= 40:
        return "HIGH"

    elif score >= 20:
        return "MEDIUM"

    else:
        return "LOW"


def calculate_contributor_risk(
    findings,
    metadata_path
):

    contributors = load_contributors(
        metadata_path
    )

    contributor_map = create_contributor_map(
        contributors
    )

    risk_data = {}

    for finding in findings:

        image = finding.get(
            "image",
            "unknown_image"
        )

        original_image = find_original_image(
            image,
            contributor_map
        )

        # ----------------------------------
        # Get contributor information
        # ----------------------------------

        if original_image is not None:

            contributor_info = contributor_map[
                original_image
            ]

            contributor_name = contributor_info[
                "contributor"
            ]

            batch = contributor_info[
                "batch"
            ]

            source = contributor_info[
                "source"
            ]

        else:

            contributor_name = "Unknown"
            batch = "Unknown"
            source = "Unknown"

        # ----------------------------------
        # Calculate finding weight
        # ----------------------------------

        finding_type = finding.get(
            "type",
            "unknown"
        )

        weight = RISK_WEIGHTS.get(
            finding_type,
            10
        )

        # ----------------------------------
        # Create contributor record
        # ----------------------------------

        if contributor_name not in risk_data:

            risk_data[contributor_name] = {

                "contributor":
                    contributor_name,

                "batch":
                    batch,

                "source":
                    source,

                "risk_score":
                    0,

                "total_findings":
                    0,

                "findings":
                    []

            }

        # ----------------------------------
        # Add risk
        # ----------------------------------

        risk_data[
            contributor_name
        ]["risk_score"] += weight

        risk_data[
            contributor_name
        ]["total_findings"] += 1

        risk_data[
            contributor_name
        ]["findings"].append({

            "image":
                image,

            "original_image":
                original_image,

            "type":
                finding_type,

            "severity":
                finding.get(
                    "severity",
                    "UNKNOWN"
                ),

            "reason":
                finding.get(
                    "reason",
                    ""
                )

        })

    # --------------------------------------
    # Build final result
    # --------------------------------------

    results = []

    for contributor, data in risk_data.items():

        score = min(
            data["risk_score"],
            100
        )

        data["risk_score"] = score

        data["risk_level"] = get_risk_level(
            score
        )

        results.append(data)

    return results