TOKEN = ''
bot_name = ''
admin_id = [
manager_id = 
order_channel = 

all_template_types = {
    'VISTA EUR': {'allowed_pairs': ['RUB', 'BYN', 'THB'],
                  'sign': 'VST €'},
    'VISTA USD': {'allowed_pairs': ['RUB', 'BYN', 'THB'],
                  'sign': 'VST $'},
    'RUB': {'allowed_pairs': ['VISTA EUR', 'VISTA USD', 'THB'],
            'sign': '₽'},
    'BYN': {'allowed_pairs': ['VISTA EUR', 'VISTA USD'],
            'sign': 'BYN'},
    'THB': {'allowed_pairs': ['VISTA EUR', 'VISTA USD', 'RUB'],
            'sign': '฿'},
                      }

convert = {
    ('VISTA EUR', 'RUB'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'VISTA EUR'
    },
    ('VISTA EUR', 'BYN'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'VISTA EUR'
    },
    ('VISTA EUR', 'THB'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'VISTA EUR'
    },
    ('VISTA USD', 'RUB'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'VISTA USD'
    },
    ('VISTA USD', 'BYN'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'VISTA USD'
    },
    ('VISTA USD', 'THB'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'VISTA USD'
    },
    ('RUB', 'VISTA EUR'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'VISTA EUR'
    },
    ('RUB', 'VISTA USD'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'VISTA USD'
    },
    ('RUB', 'THB'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'TBH'
    },
    ('BYN', 'VISTA EUR'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'VISTA EUR'
    },
    ('BYN', 'VISTA USD'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'VISTA USD'
    },
    ('THB', 'VISTA EUR'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'VISTA EUR'
    },
    ('THB', 'VISTA USD'): {
        'convert': lambda amount, rate: round(amount / rate, 2),
        'commission': 'VISTA USD'
    },
    ('THB', 'RUB'): {
        'convert': lambda amount, rate: round(amount * rate, 2),
        'commission': 'THB'
    }
}

order_stage = [None, 'first_pay', 'first_approve', 'second_pay', 'second_approve', 'wait_closing', 'closed']
