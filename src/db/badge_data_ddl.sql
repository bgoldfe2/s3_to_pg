DROP TABLE IF EXISTS public.BadgeData;
DROP TYPE IF EXISTS emp_status;

CREATE TYPE emp_status AS ENUM('IN','OUT');

CREATE TABLE public.BadgeData
(
kiosk varchar NOT NULL,
tmstamp timestamp NOT NULL,  -- Need to investigate time zones
emp_id varchar NOT NULL,
fname varchar,
middle varchar,
lname varchar NOT NULL,
emp_occupancy emp_status default 'OUT',  --<== set default to 'OUT'
CONSTRAINT BadgeData_pkey PRIMARY KEY (kiosk, tmstamp)
)
WITH (
OIDS = FALSE
)
TABLESPACE pg_default;