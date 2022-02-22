/* add AKundenbesuch to customer dashboard, only works for v11 and above */
try {
    cur_frm.dashboard.add_transactions([
        {
            'label': __('Other'),
            'items': ['Kundenbesuch']
        }
    ]);
} catch { /* do nothing for older versions */ }
