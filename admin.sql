psql postgres
sudo -u postgres psql
\list

\connect name_database

INSERT INTO res_groups_users_rel (gid, uid)
VALUES (
    (SELECT id as gid FROM res_groups WHERE res_groups.name='Settings'), 
    (SELECT id AS uid FROM res_users WHERE res_users.login='__system__')
);

INSERT INTO res_groups_users_rel (gid, uid)
VALUES (
    (SELECT res_id FROM ir_model_data WHERE module='base' AND name='group_system'), 
    (SELECT id AS uid FROM res_users WHERE res_users.login='__system__')
);


select psa.query from pg_locks as pg left join pg_stat_activity as psa on pg.pid=psa.pid where psa.datname='db_12';