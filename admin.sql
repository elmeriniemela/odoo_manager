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

DELETE FROM ir_ui_view WHERE arch_db LIKE '%is_company_account%' AND model='res.partner.bank';

select psa.query from pg_locks as pg left join pg_stat_activity as psa on pg.pid=psa.pid where psa.datname='db_12';


SELECT sanitized_acc_number, count(*) as lkm FROM res_partner_bank GROUP BY sanitized_acc_number HAVING count(*) > 1;

UPDATE res_partner_bank SET res_partner_bank.company_id=account_invoice.company_id FROM res_partner_bank INNER JOIN account_invoice WHERE res_partner_bank.id=account_invoice.partner_bank_id; 
UPDATE res_partner_bank SET company_id=account_invoice.company_id FROM account_invoice WHERE res_partner_bank.id=account_invoice.partner_bank_id;
SELECT id FROM account_invoice WHERE company_id != (SELECT company_id FROM res_partner_bank WHERE id = account_invoice.partner_bank_id)

-- Multi company errors
SELECT id, company_id, acc_number FROM res_partner_bank WHERE id in (
    SELECT partner_bank_id FROM account_invoice WHERE company_id != (
        SELECT company_id FROM res_partner_bank WHERE id = account_invoice.partner_bank_id
    )
);

UPDATE account_invoice SET partner_bank_id=NULL WHERE company_id != (SELECT company_id FROM res_partner_bank WHERE id = account_invoice.partner_bank_id) AND state='draft';