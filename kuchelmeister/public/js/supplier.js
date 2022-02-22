/* add Anmeldung Subakkordant to supplier dashboard, only works for v11 and above */
try {
    cur_frm.dashboard.add_transactions([
        {
            'label': __('Other'),
            'items': ['Anmeldung Subakkordant']
        }
    ]);
} catch { /* do nothing for older versions */ }
