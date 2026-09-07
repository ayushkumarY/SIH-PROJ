import json

from provenance.digital_signature import sign_data


RECORD_FILE = "../reports/inference_record.json"


print("\n================================")
print("     SIGN PROVENANCE RECORD")
print("================================")


with open(
    RECORD_FILE,
    "r",
    encoding="utf-8"
) as file:

    record = json.load(file)


data_to_sign = json.dumps(
    record,
    sort_keys=True,
    separators=(",", ":")
)


signature = sign_data(data_to_sign)


record["digital_signature"] = signature


with open(
    RECORD_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        record,
        file,
        indent=4
    )


print("\nDigital signature created.")

print("\nSignature:")
print(signature[:80] + "...")

print("\nRecord updated:")
print(RECORD_FILE)

print("\n================================")