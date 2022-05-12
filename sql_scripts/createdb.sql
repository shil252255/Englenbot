create table users(
    id bigint primary key,
    is_bot boolean,
    first_name varchar,
    last_name varchar,
    username varchar,
    language_code varchar,
    reg_date timestamp with time zone
);

create table users_progress(
    user_id bigint,
    word varchar,
    status integer,
    next_training timestamp with time zone,
    last_result varchar
);

create table main_dict(
    word varchar,
    translation varchar
);
