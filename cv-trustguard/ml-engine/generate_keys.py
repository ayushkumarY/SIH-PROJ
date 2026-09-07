from provenance.digital_signature import generate_keys


print("\n================================")
print("       DIGITAL KEY SETUP")
print("================================")

generate_keys()

print("\nPrivate key:")
print("../models/keys/private_key.pem")

print("\nPublic key:")
print("../models/keys/public_key.pem")

print("\n================================")