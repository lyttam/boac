SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE advisor_watchlists (
    watchlist_owner_uid character varying(80) NOT NULL,
    sid character varying(80) NOT NULL
);
ALTER TABLE advisor_watchlists OWNER TO boac;
ALTER TABLE ONLY advisor_watchlists
    ADD CONSTRAINT advisor_watchlists_pkey PRIMARY KEY (watchlist_owner_uid, sid);


CREATE TABLE alert_views (
    alert_id integer NOT NULL,
    viewer_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    dismissed_at timestamp with time zone
);
ALTER TABLE alert_views OWNER TO boac;
ALTER TABLE ONLY alert_views
    ADD CONSTRAINT alert_views_pkey PRIMARY KEY (alert_id, viewer_id);
CREATE INDEX alert_views_alert_id_idx ON alert_views USING btree (alert_id);
CREATE INDEX alert_views_viewer_id_idx ON alert_views USING btree (viewer_id);


CREATE TABLE alerts (
    id integer NOT NULL,
    sid character varying(80) NOT NULL,
    alert_type character varying(80) NOT NULL,
    key character varying(255) NOT NULL,
    message text NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE alerts OWNER TO boac;
CREATE SEQUENCE alerts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE alerts_id_seq OWNER TO boac;
ALTER SEQUENCE alerts_id_seq OWNED BY alerts.id;
ALTER TABLE ONLY alerts ALTER COLUMN id SET DEFAULT nextval('alerts_id_seq'::regclass);
ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);
ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_sid_alert_type_key_unique_constraint UNIQUE (sid, alert_type, key);
CREATE INDEX alerts_sid_idx ON alerts USING btree (sid);


CREATE TABLE athletics (
    group_code character varying(80) NOT NULL,
    group_name character varying(255) NOT NULL,
    team_code character varying(80) NOT NULL,
    team_name character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE athletics OWNER TO boac;
ALTER TABLE ONLY athletics
    ADD CONSTRAINT athletics_pkey PRIMARY KEY (group_code);


CREATE TABLE authorized_users (
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    id integer NOT NULL,
    uid character varying(255) NOT NULL,
    is_advisor boolean,
    is_admin boolean,
    is_director boolean
);
ALTER TABLE authorized_users OWNER TO boac;
CREATE SEQUENCE authorized_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE authorized_users_id_seq OWNER TO boac;
ALTER SEQUENCE authorized_users_id_seq OWNED BY authorized_users.id;
ALTER TABLE ONLY authorized_users ALTER COLUMN id SET DEFAULT nextval('authorized_users_id_seq'::regclass);
ALTER TABLE ONLY authorized_users
    ADD CONSTRAINT authorized_users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY authorized_users
    ADD CONSTRAINT authorized_users_uid_key UNIQUE (uid);


CREATE TABLE cohort_filter_owners (
    cohort_filter_id integer NOT NULL,
    user_id integer NOT NULL
);
ALTER TABLE cohort_filter_owners OWNER TO boac;
ALTER TABLE ONLY cohort_filter_owners
    ADD CONSTRAINT cohort_filter_owners_pkey PRIMARY KEY (cohort_filter_id, user_id);


CREATE TABLE cohort_filters (
    id integer NOT NULL,
    label character varying(255) NOT NULL,
    filter_criteria jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE cohort_filters OWNER TO boac;
CREATE SEQUENCE cohort_filters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE cohort_filters_id_seq OWNER TO boac;
ALTER SEQUENCE cohort_filters_id_seq OWNED BY cohort_filters.id;
ALTER TABLE ONLY cohort_filters ALTER COLUMN id SET DEFAULT nextval('cohort_filters_id_seq'::regclass);
ALTER TABLE ONLY cohort_filters
    ADD CONSTRAINT cohort_filters_pkey PRIMARY KEY (id);


CREATE TABLE json_cache (
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    id integer NOT NULL,
    key character varying NOT NULL,
    json jsonb
);
ALTER TABLE json_cache OWNER TO boac;
CREATE SEQUENCE json_cache_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE json_cache_id_seq OWNER TO boac;
ALTER SEQUENCE json_cache_id_seq OWNED BY json_cache.id;
ALTER TABLE ONLY json_cache ALTER COLUMN id SET DEFAULT nextval('json_cache_id_seq'::regclass);
ALTER TABLE ONLY json_cache
    ADD CONSTRAINT json_cache_key_key UNIQUE (key);
ALTER TABLE ONLY json_cache
    ADD CONSTRAINT json_cache_pkey PRIMARY KEY (id);


CREATE TABLE normalized_cache_student_majors (
    sid character varying(80) NOT NULL,
    major character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE normalized_cache_student_majors OWNER TO boac;
ALTER TABLE ONLY normalized_cache_student_majors
    ADD CONSTRAINT normalized_cache_student_majors_pkey PRIMARY KEY (sid, major);
CREATE INDEX normalized_cache_student_majors_major_idx ON normalized_cache_student_majors USING btree (major);
CREATE INDEX normalized_cache_student_majors_sid_idx ON normalized_cache_student_majors USING btree (sid);


CREATE TABLE normalized_cache_students (
    sid character varying(80) NOT NULL,
    gpa numeric,
    level character varying(9),
    units numeric,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE normalized_cache_students OWNER TO boac;
ALTER TABLE ONLY normalized_cache_students
    ADD CONSTRAINT normalized_cache_students_pkey PRIMARY KEY (sid);
CREATE INDEX normalized_cache_students_gpa_idx ON normalized_cache_students USING btree (gpa);
CREATE INDEX normalized_cache_students_level_idx ON normalized_cache_students USING btree (level);
CREATE INDEX normalized_cache_students_units_idx ON normalized_cache_students USING btree (units);


CREATE TABLE student_athletes (
    group_code character varying(80) NOT NULL,
    sid character varying(80) NOT NULL
);
ALTER TABLE student_athletes OWNER TO boac;
ALTER TABLE ONLY student_athletes
    ADD CONSTRAINT student_athletes_pkey PRIMARY KEY (group_code, sid);


CREATE TABLE students (
    sid character varying(80) NOT NULL,
    uid character varying(80),
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    in_intensive_cohort boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE students OWNER TO boac;
ALTER TABLE ONLY students
    ADD CONSTRAINT students_pkey PRIMARY KEY (sid);


ALTER TABLE ONLY advisor_watchlists
    ADD CONSTRAINT advisor_watchlists_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;
ALTER TABLE ONLY advisor_watchlists
    ADD CONSTRAINT advisor_watchlists_watchlist_owner_uid_fkey FOREIGN KEY (watchlist_owner_uid) REFERENCES authorized_users(uid) ON DELETE CASCADE;


ALTER TABLE ONLY alert_views
    ADD CONSTRAINT alert_views_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE;
ALTER TABLE ONLY alert_views
    ADD CONSTRAINT alert_views_viewer_id_fkey FOREIGN KEY (viewer_id) REFERENCES authorized_users(id) ON DELETE CASCADE;


ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;


ALTER TABLE ONLY cohort_filter_owners
    ADD CONSTRAINT cohort_filter_owners_cohort_filter_id_fkey FOREIGN KEY (cohort_filter_id) REFERENCES cohort_filters(id) ON DELETE CASCADE;
ALTER TABLE ONLY cohort_filter_owners
    ADD CONSTRAINT cohort_filter_owners_user_id_fkey FOREIGN KEY (user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;


ALTER TABLE ONLY normalized_cache_student_majors
    ADD CONSTRAINT normalized_cache_student_majors_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;
ALTER TABLE ONLY normalized_cache_students
    ADD CONSTRAINT normalized_cache_students_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;


ALTER TABLE ONLY student_athletes
    ADD CONSTRAINT student_athletes_group_code_fkey FOREIGN KEY (group_code) REFERENCES athletics(group_code) ON DELETE CASCADE;
ALTER TABLE ONLY student_athletes
    ADD CONSTRAINT student_athletes_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;
