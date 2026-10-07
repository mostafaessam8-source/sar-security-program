import json, base64, sys
d='/tmp/claude-0/-home-user/0d8cf00c-df50-59d0-89bb-befade0f854d/scratchpad/p6/'
t=open(d+'pres_template.html').read()
data=open(d+'pres_data.json').read()
logo=open('/tmp/w/logo.b64').read().strip()
logow=base64.b64encode(open(d+'../deck/logo_white.png','rb').read()).decode()
chart=open('/tmp/w/package/dist/chart.umd.js').read()
out=t.replace('%%LOGO%%',logo).replace('%%LOGOW%%',logow).replace('%%DATA%%',data).replace('%%CHART%%',chart.replace('</script>','<\\/script>'))
open(d+'presentation_built.html','w').write(out)
print(len(out)//1024,'KB')
