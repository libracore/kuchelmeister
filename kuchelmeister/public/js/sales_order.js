/* add Anmeldung Subakkordant to sales order dashboard, only works for v11 and above */
try {
    cur_frm.dashboard.add_transactions([
        {
            'label': __('Other'),
            'items': ['Anmeldung Subakkordant']
        }
    ]);
} catch { /* do nothing for older versions */ }
