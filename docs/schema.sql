--Assumption:
--Each Customer can have max 50 fields
--Each Customer can have multiples clientIds(apps)
--There would be separate stack at Customer(/Tenant) level and NOT at ClientId level.
--Note:
--CustomerId is added to all tables for Row Level Security at Customer(/Tenant) level

-- customer table - New rows added to this table when new customer is onboarded.
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(64),
    company_name VARCHAR(64) NOT NULL,
    contact_name VARCHAR(64) NOT NULL,
    email VARCHAR(320),
    phone VARCHAR(32),
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY (customer_id)
);

-- customer specific metadata.
CREATE TABLE IF NOT EXISTS customer_metadata (
    customer_id VARCHAR(64) REFERENCES customers,
    fields_checksum VARCHAR(128), -- checksum/hash calculated from all active fields belonging to the customer. Used to check if anything has changed/field cache need to be udpated.
    scopes_checksum VARCHAR(128), -- checksum/hash calculated from all active fields belonging to the customer. Used to check if anything has changed/field cache need to be udpated.
    lockbox_id VARCHAR(64),
    lockbox_path VARCHAR(1024), -- id and path are currently treated separatly in our code.
    key_provider VARCHAR(16), -- KMS/HSM
    key_id VARCHAR(64),
    customer_prefix VARCHAR(5),
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY (customer_id)
);

-- charset definitions
CREATE TABLE IF NOT EXISTS charsets (
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    charset_id SERIAL,
    char_set_base INTEGER,
    charset_friendly_name VARCHAR(64),
    charset VARCHAR(300),
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY (charset_id)
);

-- enum type for status, deprecated means tok is disabled, but detok is enabled
DO $$ BEGIN
    CREATE TYPE status_type AS ENUM ('active', 'deprecated', 'disabled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- contains the fields defined by every Customer/Tenant
CREATE TABLE IF NOT EXISTS fields(
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    field_name VARCHAR(100),
    field_version INTEGER,
    field_version_status status_type NOT NULL,
    charset_id INTEGER REFERENCES charsets,
    customer_field_description JSONB, -- contains details of what the user has slected from the UI.
    field_definition JSONB, -- contains the actual field definition used by the tokenize algorithm. Also contains shuflfe table and crypto paths
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY (customer_id, field_name, field_version)
);

-- contains details about client apps, as defined in DevEx
CREATE TABLE IF NOT EXISTS client_apps (
    client_app_id VARCHAR(32),
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    client_app_name VARCHAR(32),
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    authentication JSONB,
    PRIMARY KEY (client_app_id)
);

-- policies are permissions to query the API for specific fields
CREATE TABLE IF NOT EXISTS policies (
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    policy_id SERIAL,
    policy_name VARCHAR(100),
    UNIQUE (customer_id,policy_name),
    is_enabled BOOLEAN,
    policy_description VARCHAR(500),
    field_selections JSONB,
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY(policy_id)
);

-- policy_assignments are used to assing multiple policies to one client app
CREATE TABLE IF NOT EXISTS policy_assignments (
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    policy_assignment_id SERIAL,
    client_app_id VARCHAR(32) REFERENCES client_apps,
    is_enabled BOOLEAN,
    policy_id_list INTEGER[],
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY(policy_assignment_id)
);

-- user_entitlements are permissions for interacting with the configuration service ( UI and API )
CREATE TABLE IF NOT EXISTS user_entitlements (
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    entitlement_id SERIAL,
    entitlement_name VARCHAR(64),
    entitlement_logic JSONB,
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY(entitlement_id)
);

-- a user_roles are groups of entitlements that define a certain role that can be assigned to a user.
CREATE TABLE IF NOT EXISTS user_roles (
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    role_id SERIAL,
    role_name VARCHAR(64),
    entitlement_id_list INTEGER[],
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY(role_id)
);

-- users are human users that interact with the configuration service
CREATE TABLE IF NOT EXISTS users (
    customer_id VARCHAR(64) REFERENCES customer_metadata,
    user_id VARCHAR(64),
    role_id_list INTEGER[],
    created_on TIMESTAMP,
    created_by VARCHAR(64),
    last_modified TIMESTAMP,
    last_modified_by VARCHAR(64),
    PRIMARY KEY(user_id)
);

-- enum type for field secret type
DO $$ BEGIN
    CREATE TYPE key_type AS ENUM ('field_secret', 'secret_salt', 'secret_table');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- enum type for field key status
DO $$ BEGIN
    CREATE TYPE key_status AS ENUM ('active', 'inactive', 'unassigned');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS secret_keys (
    secret_key_name VARCHAR(64),
    secret_key_type key_type NOT NULL,
    secret_key_status key_status NOT NULL,
    created_on TIMESTAMP,
    last_modified TIMESTAMP,
    PRIMARY KEY(secret_key_name)
);