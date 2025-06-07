def predict_reimbursement(days, miles, receipts):
    # Features
    inv_receipts = 1 / (1 + receipts)
    three_way = days * miles * receipts / 1000
    log_receipts = np.log1p(receipts)
    days_miles = days * miles
    receipts_sq_scaled = receipts ** 2 / 1e6
    days_receipts = days * receipts
    miles_receipts_scaled = miles * receipts / 1000
    five_day = 1 if days == 5 else 0
    ends49 = 1 if int(receipts * 100) % 100 == 49 else 0
    ends99 = 1 if int(receipts * 100) % 100 == 99 else 0
    
    # Decision tree
if log_receipts <= 6.720334:
    if days_miles <= 2070.000000:
        if days_receipts <= 562.984985:
            if days_miles <= 566.000000:
                return 287.10
            else:
                return 581.58
        else:
            if days_receipts <= 3089.010010:
                if days_miles <= 1310.500000:
                    if receipts <= 461.820007:
                        return 557.93
                    else:
                        return 643.31
                else:
                    return 750.45
            else:
                return 876.59
    else:
        if three_way <= 2172.216919:
            if days_miles <= 4940.000000:
                if three_way <= 1258.291565:
                    if days <= 5.500000:
                        return 770.85
                    else:
                        return 864.46
                else:
                    if receipts <= 506.684998:
                        return 941.68
                    else:
                        return 1012.53
            else:
                return 1145.20
        else:
            if three_way <= 3762.473267:
                if miles <= 771.000000:
                    return 1163.81
                else:
                    return 1240.19
            else:
                return 1442.54
else:
    if three_way <= 6405.638672:
        if three_way <= 1253.387817:
            if days_receipts <= 9442.660156:
                if inv_receipts <= 0.000923:
                    if days_miles <= 449.000000:
                        return 1196.52
                    else:
                        return 1296.70
                else:
                    return 1067.12
            else:
                return 1505.52
        else:
            if days_receipts <= 5494.430176:
                if three_way <= 2917.123047:
                    if miles_receipts_scaled <= 834.080933:
                        return 1297.57
                    else:
                        return 1392.04
                else:
                    return 1488.02
            else:
                if days_receipts <= 13199.189941:
                    if miles <= 518.500000:
                        if days_miles <= 2517.500000:
                            if three_way <= 2272.934448:
                                return 1463.72
                            else:
                                return 1523.63
                        else:
                            return 1410.89
                    else:
                        if three_way <= 5415.271729:
                            return 1571.23
                        else:
                            return 1618.87
                else:
                    if days <= 10.500000:
                        return 1588.76
                    else:
                        return 1671.65
    else:
        if days_miles <= 6483.000000:
            if receipts_sq_scaled <= 4.168643:
                if days <= 7.500000:
                    return 1765.20
                else:
                    return 1693.27
            else:
                if log_receipts <= 7.739514:
                    return 1642.03
                else:
                    return 1677.18
        else:
            if miles <= 995.000000:
                if days <= 12.500000:
                    if miles <= 774.000000:
                        return 1774.64
                    else:
                        if receipts <= 1758.599976:
                            return 1876.53
                        else:
                            return 1802.38
                else:
                    return 1900.41
            else:
                if miles_receipts_scaled <= 1842.686523:
                    return 2033.30
                else:
                    return 1882.41