def _abv(og, fg):
    return (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794)


def _brix_to_og(brix):
    return (brix / (258.6 - ((brix / 258.2) * 227.1))) + 1

def _hydro_temp_adj(mg, mtemp, ctemp):
    ag = mg * ((1.00130346 - 0.000134722124 * mtemp + 0.00000204052596 * mtemp**2 - 0.00000000232820948 * mtemp**3) /
               (1.00130346 - 0.000134722124 * ctemp + 0.00000204052596 * ctemp**2 - 0.00000000232820948 * ctemp**3))
    return ag

def calc_abv(args):
    usage = 'Usage: .abv <OG> <FG>'
    if len(args) != 2:
        return usage

    try:
        og = float(args[0])
        fg = float(args[1])
        return 'ABV is %.1f' % _abv(og, fg)

    except Exception:
        # not passed numbers
        return usage


def brix_sg(args):
    usage = 'Usage: .brix <Original BRIX> (<Final BRIX>)'
    if len(args) < 1 or len(args) > 2:
        return usage

    if len(args) == 1:
        try:
            brix = float(args[0])
            return 'OG is %.3f' % _brix_to_og(brix)
        except Exception:
            # not passed numbers
            return usage

    if len(args) == 2:
        try:
            obrix = float(args[0])
            fbrix = float(args[1])
            sg = _brix_to_og(obrix)
            fg = (1 -
                  (0.004493 * obrix) + (0.011774 * fbrix) +
                  (0.00027581 * obrix ** 2) - (0.0012717 * fbrix ** 2) -
                  (0.00000728 * obrix ** 3) + (0.000063293 * fbrix ** 3))
            abv = _abv(sg, fg)

            message = ('OG: %(og).3f; FG: %(fg).3f, ABV: %(abv).1f' %
                       {'og': sg, 'fg': fg, 'abv': abv})
            return message

        except Exception:
            # not passed numbers
            return usage

def hydro_adj(args):
    usage = 'Usage: .hydrometer <Measured Gravity> <Measured Temp> <Calibrated Temp>'
    if len(args) != 3:
        return usage

    try:
        mg = float(args[0])
        mtemp = float(args[1])
        ctemp = float(args[2])
        return 'Adjusted Gravity is %.3f' % _hydro_temp_adj(mg, mtemp, ctemp)

    except Exception:
        # not passed numbers
        return usage
    
def untappd(args):
    import os
    import requests
    import json
    client_id = os.environ["UNTAPPD_CLIENT_ID"]
    client_secret = os.environ["UNTAPPD_CLIENT_SECRET"]

    usage = 'Usage: .untappd <brewery name> <beer name>'
    url = 'https://api.untappd.com/v4'
    user_agent = 'homebrew.chat (' + client_id + ')'
    headers = {'User-Agent': user_agent}

    query = " ".join(args)
  
    try:
        sres = requests.get(url + '/search/beer', params={'client_id': client_id, 'client_secret': client_secret, 'q': query}, headers=headers)
        sjson = sres.json()
        bid = sjson['response']['beers']['items'][0]['beer']['bid']
    
    except Exception:
        # could not find a beer
        return usage
    
    try:
        bres = requests.get(url + '/beer/info/' + str(bid), params={'client_id': client_id, 'client_secret': client_secret}, headers=headers)
        bjson = bres.json()
        heading = '*' + bjson['response']['beer']['brewery']['brewery_name'] + ' ' +  bjson['response']['beer']['beer_name'] + '*'
        rating = '*Average Rating*\n' + str(round(bjson['response']['beer']['rating_score'], 2)) + ' from ' + str(bjson['response']['beer']['rating_count']) + ' opinions'
        text = heading + '\n' + rating
        desc_text = '*Style:* ' + bjson['response']['beer']['beer_style'] + '\n'
        desc_text += '*IBU:* ' + str(bjson['response']['beer']['beer_ibu']) + '    ' + '*ABV:* ' + str(round(bjson['response']['beer']['beer_abv'], 1)) + '\n'
        desc_text += bjson['response']['beer']['beer_description']
        blocks = json.dumps([{
                   "type": "section",
                   "text": {
                     "type": "mrkdwn",
                     "text": heading
                   }
                 },
                 {
                   "type": "section",
                   "block_id": "section567",
                   "text": {
                     "type": "mrkdwn",
                     "text": desc_text
                   },
                   "accessory": {
                     "type": "image",
                     "image_url":   bjson['response']['beer']['beer_label'],
                     "alt_text": "Beer label image"
                   }
                 },
                 {
                   "type": "section",
                   "block_id": "section789",
                   "fields": [
                     {
                       "type": "mrkdwn",
                       "text": rating
                     }
                   ]
                 }])
        response = { 'text': text, 'blocks': blocks }
        return(response)
       
    except Exception as err:
        # w t f indeed
        return usage

