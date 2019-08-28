psql postgres
sudo -u postgres psql
\list

\connect name_database


UPDATE res_users SET login='admin' WHERE login='catchall@tarfi.fi';

-- Set password to 'admin'
UPDATE res_users SET password='$pbkdf2-sha512$25000$zvkfQ6iVEiLk/N/7n5NSqg$0TyLtKt/O.Ma/TOvWJYcNsrR7v8xSA7FKBpmCjRHHpewAbz8GtDHQvCHINL7gqEhHoCegAJJe8V9DdDK/NzHwg' WHERE login='admin';


UPDATE res_users SET password='$pbkdf2-sha512$25000$W8vZW.sdQyilFOJcK2XM2Q$PiuDaZIwfraXAKaFfhNIexIOR5x4Okps2a9KzYXFIzvIJrf4S2X2.ARDU6iEMqHxJZFX856OqoyzXZSbv4kUsQ' WHERE login='jari.pajunen@taloustutkimus.fi';

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

DELETE FROM ir_ui_view WHERE arch_db LIKE '%is_commercial_entity%' AND model='res.partner';

select psa.query from pg_locks as pg left join pg_stat_activity as psa on pg.pid=psa.pid where psa.datname='tarfi';


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


SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'tarfi'
  AND pid <> pg_backend_pid();


UPDATE account_invoice SET partner_bank_id=NULL WHERE company_id != (SELECT company_id FROM res_partner_bank WHERE id = account_invoice.partner_bank_id) AND state='draft';



COPY res_partner(id,name,city,email,street,phone,credit_limit,einvoice_address,einvoice_operator,is_company,customer,supplier,vat,invoice_merging,invoice_merging_group_by,invoicing_day_monthly_first,invoicing_day_monthly_mid,invoicing_day_monthly_last,invoicing_day_weekly,invoicing_day,ref,invoice_delivery,type,country_id,vendor_invoice_default_account_id,parent_id)
TO '/tmp/res_partner.csv' WITH CSV HEADER DELIMITER ';';


COPY (SELECT id,name,res_id,value_reference FROM ir_property WHERE name='property_product_pricelist';)
TO '/tmp/ir_property.csv' WITH CSV HEADER DELIMITER ';';

COPY product_pricelist(id,name,code)
TO '/tmp/product_pricelist.csv' WITH CSV HEADER DELIMITER ';';

COPY (select message from ir_logging where func='Merge invoices setting from children to commercial entity')
TO '/tmp/merge_invoices.csv' WITH CSV HEADER DELIMITER ';';

UPDATE res_partner SET invoicing_day_weekly=4;
UPDATE res_partner SET invoice_merging_group_by='delivery_and_invoice';


CREATE TABLE temp_res_partners
(
  id integer,
  type character varying,
  street character varying,
  street2 character varying,
  zip character varying,
  city character varying,
  state_id integer,
  country_id integer
);

COPY temp_res_partners(id, type, street, street2, zip, city, state_id, country_id)
FROM '/opt/odoo/tarfi_partners2.csv' WITH CSV HEADER DELIMITER ';';

UPDATE res_partner
SET 
type=temp_res_partners.type,
street=temp_res_partners.street,
street2=temp_res_partners.street2,
zip=temp_res_partners.zip,
city=temp_res_partners.city,
state_id=temp_res_partners.state_id,
country_id=temp_res_partners.country_id
FROM temp_res_partners
WHERE res_partner.id=temp_res_partners.id;

DROP TABLE temp_res_partners;



UPDATE res_partner SET type='delivery' WHERE parent_id IS NOT NULL AND type='other' AND customer=True;


UPDATE
    sale_order
SET
    partner_id = commercial_partner_id
FROM
    sale_order AS sale
    INNER JOIN res_partner AS partner
        ON sale.partner_id = partner.id
;