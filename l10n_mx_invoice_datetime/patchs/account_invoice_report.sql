DROP VIEW IF EXISTS account_invoice_report ;

create or replace view account_invoice_report as (
                 select min(ail.id) as id,
                    CAST( ai.invoice_datetime AS DATE) as date,
                    to_char(ai.invoice_datetime, 'YYYY') as year,
                    to_char(ai.invoice_datetime, 'MM') as month,
                    to_char(ai.invoice_datetime, 'YYYY-MM-DD') as day,
                    ail.product_id,
                    ai.partner_id as partner_id,
                    ai.payment_term as payment_term,
                    ai.period_id as period_id,
                    (case when u.uom_type not in ('reference') then
                        (select name from product_uom where uom_type='reference' and active and category_id=u.category_id LIMIT 1)
                    else
                        u.name
                    end) as uom_name,
                    ai.currency_id as currency_id,
                    ai.journal_id as journal_id,
                    ai.fiscal_position as fiscal_position,
                    ai.user_id as user_id,
                    ai.company_id as company_id,
                    count(ail.*) as nbr,
                    ai.type as type,
                    ai.state,
                    pt.categ_id,
                    ai.date_due as date_due,
                    ai.address_contact_id as address_contact_id,
                    ai.address_invoice_id as address_invoice_id,
                    ai.account_id as account_id,
                    ai.partner_bank_id as partner_bank_id,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         ail.quantity / u.factor * -1
                        else
                         ail.quantity / u.factor
                        end) as product_qty,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         ail.quantity*ail.price_unit * -1
                        else
                         ail.quantity*ail.price_unit
                        end) / cr.rate as price_total,
                    sum(case when ai.type in ('out_refund','in_invoice') then
                         ai.amount_total * -1
                        else
                         ai.amount_total
                         end) / (CASE WHEN 
                              (select count(l.id) from account_invoice_line as l
                               left join account_invoice as a ON (a.id=l.invoice_id)
                               where a.id=ai.id) <> 0 
                            THEN 
                              (select count(l.id) from account_invoice_line as l
                               left join account_invoice as a ON (a.id=l.invoice_id)
                               where a.id=ai.id) 
                            ELSE 1 
                            END) / cr.rate as price_total_tax,
                    (case when ai.type in ('out_refund','in_invoice') then
                      sum(ail.quantity*ail.price_unit*-1)
                    else
                      sum(ail.quantity*ail.price_unit)
                    end) / (CASE WHEN
                         (case when ai.type in ('out_refund','in_invoice') 
                          then sum(ail.quantity/u.factor*-1)
                          else sum(ail.quantity/u.factor) end) <> 0 
                       THEN 
                         (case when ai.type in ('out_refund','in_invoice') 
                          then sum(ail.quantity/u.factor*-1)
                          else sum(ail.quantity/u.factor) end) 
                       ELSE 1 
                       END)
                     / cr.rate as price_average,

                    cr.rate as currency_rate,
                    sum((select extract(epoch from avg(date_trunc('day',aml.date_created)-date_trunc('day',l.create_date)))/(24*60*60)::decimal(16,2)
                        from account_move_line as aml
                        left join account_invoice as a ON (a.move_id=aml.move_id)
                        left join account_invoice_line as l ON (a.id=l.invoice_id)
                        where a.id=ai.id)) as delay_to_pay,
                    sum((select extract(epoch from avg(date_trunc('day',a.date_due)-date_trunc('day',a.invoice_datetime)))/(24*60*60)::decimal(16,2)
                        from account_move_line as aml
                        left join account_invoice as a ON (a.move_id=aml.move_id)
                        left join account_invoice_line as l ON (a.id=l.invoice_id)
                        where a.id=ai.id)) as due_delay,
                    (case when ai.type in ('out_refund','in_invoice') then
                      ai.residual * -1
                    else
                      ai.residual
                    end)/ (CASE WHEN 
                        (select count(l.id) from account_invoice_line as l
                         left join account_invoice as a ON (a.id=l.invoice_id)
                         where a.id=ai.id) <> 0 
                       THEN
                        (select count(l.id) from account_invoice_line as l
                         left join account_invoice as a ON (a.id=l.invoice_id)
                         where a.id=ai.id) 
                       ELSE 1 
                       END) / cr.rate as residual
                from account_invoice_line as ail
                left join account_invoice as ai ON (ai.id=ail.invoice_id)
                left join product_template pt on (pt.id=ail.product_id)
                left join product_uom u on (u.id=ail.uos_id),
                res_currency_rate cr
                where cr.id in (select id from res_currency_rate cr2  where (cr2.currency_id = ai.currency_id)
                and ((ai.invoice_datetime is not null and cr.name <= ai.invoice_datetime) or (ai.invoice_datetime is null and cr.name <= NOW())) limit 1)
                group by ail.product_id,
                    ai.invoice_datetime,
                    ai.id,
                    cr.rate,
                    to_char(ai.invoice_datetime, 'YYYY'),
                    to_char(ai.invoice_datetime, 'MM'),
                    to_char(ai.invoice_datetime, 'YYYY-MM-DD'),
                    ai.partner_id,
                    ai.payment_term,
                    ai.period_id,
                    u.name,
                    ai.currency_id,
                    ai.journal_id,
                    ai.fiscal_position,
                    ai.user_id,
                    ai.company_id,
                    ai.type,
                    ai.state,
                    pt.categ_id,
                    ai.date_due,
                    ai.address_contact_id,
                    ai.address_invoice_id,
                    ai.account_id,
                    ai.partner_bank_id,
                    ai.residual,
                    ai.amount_total,
                    u.uom_type,
                    u.category_id
            )
;
