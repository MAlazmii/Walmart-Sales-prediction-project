const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM} = require('jsdom');
const root = path.join(__dirname, '..');
const inventory = [{Store:'1',Dept:'1',Date:'2024-01-01',IsHoliday:'False',Last_Known_Inventory:'10'}];
function setup() {
  const dom = new JSDOM(fs.readFileSync(path.join(root,'index.html'),'utf8'), {runScripts:'outside-only', url:'http://localhost/'});
  const w = dom.window, calls = [], alerts = [];
  w.console.log=()=>{}; w.console.error=()=>{};
  w.alert = message => alerts.push(message);
  w.Chart = class {destroy(){} update(){}};
  w.fetch = async (url, options={}) => {
    calls.push({url,body:options.body && JSON.parse(options.body)});
    return {ok:true,json:async()=>url.includes('/get_data')?inventory:{prediction:123,message:'Email sent successfully'}};
  };
  for (const script of w.document.querySelectorAll('script[src="script.js"]')) w.eval(fs.readFileSync(path.join(root,'script.js'),'utf8'));
  w.document.getElementById('Type_A').click();
  const submit = async id => {w.document.getElementById(id).dispatchEvent(new w.Event('submit',{cancelable:true})); await new Promise(setImmediate);};
  return {w,calls,alerts,submit,close:()=>w.close()};
}
test('one form submission makes one prediction request',async()=>{const s=setup();try{await s.submit('predictionForm');assert.equal(s.calls.filter(x=>x.url.endsWith('/predict')).length,1);}finally{s.close();}});
test('holiday selections become the correct numeric feature',async()=>{const s=setup();try{await s.submit('predictionForm');assert.equal(s.calls[0].body.isHoliday,0);s.w.document.getElementById('isHoliday').value='true';await s.submit('predictionForm');assert.equal(s.calls.at(-1).body.isHoliday,1);}finally{s.close();}});
test('store choices appear once and radio types are mutually exclusive',()=>{const s=setup();try{assert.equal(s.w.document.getElementById('storeSelect').options.length,45);s.w.document.getElementById('Type_B').click();assert.equal(s.w.document.getElementById('Type_A').checked,false);assert.equal(s.w.document.getElementById('Type_B').checked,true);}finally{s.close();}});
test('email includes the fetched inventory records',async()=>{const s=setup();try{await s.submit('inventory_form');s.w.document.getElementById('email').value='reviewer@example.com';await s.submit('email-form');const emails=s.calls.filter(x=>x.url.endsWith('/send-email'));assert.equal(emails.length,1);assert.deepEqual(emails[0].body.inventoryData,[{store:'1',dept:'1',date:'2024-01-01',isHoliday:'False',inventory:'10'}]);}finally{s.close();}});
test('a failed inventory lookup does not email stale records',async()=>{const s=setup();try{await s.submit('inventory_form');const fetch=s.w.fetch;s.w.fetch=async(url,options)=>url.includes('/get_data')?{ok:false,json:async()=>({error:'unavailable'})}:fetch(url,options);await s.submit('inventory_form');await s.submit('email-form');assert.deepEqual(s.calls.at(-1).body.inventoryData,[]);}finally{s.close();}});
test('failed prediction does not display undefined as a result',async()=>{const s=setup();try{s.w.fetch=async()=>({ok:false,json:async()=>({error:'Prediction unavailable'})});await s.submit('predictionForm');assert.match(s.w.document.getElementById('predictionResult').textContent,/unavailable/i);assert.doesNotMatch(s.w.document.getElementById('predictionResult').textContent,/undefined/);}finally{s.close();}});
