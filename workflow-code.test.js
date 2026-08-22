'use strict';

const assert = require('assert');
const workflow = require('./lead_intake_workflow.json');

const parseNode = workflow.nodes.find(node => node.name === 'Parse qualification');
assert.ok(parseNode, 'parse node exists');
const execute = new Function('$json', '$', parseNode.parameters.jsCode);

function run(modelText, lead) {
  const result = execute(
    { content: [{ text: modelText }] },
    function (name) {
      assert.strictEqual(name, 'Lead form webhook');
      return { first: function () { return { json: { body: lead } }; } };
    }
  );
  assert.ok(Array.isArray(result) && result.length === 1);
  return result[0].json;
}

const valid = run('{"score":8,"reason":"clear fit","suggested_reply":"Thanks for the details."}', {
  name: 'Sample lead',
  email: 'lead@example.com'
});
assert.strictEqual(valid.score, 8);
assert.strictEqual(valid.qualification_valid, true);
assert.strictEqual(valid.needs_review, false);
assert.strictEqual(valid.suggested_reply, 'Thanks for the details.');

for (const candidate of [
  run('not json', { name: 'Sample lead', email: 'lead@example.com' }),
  run('{"score":12,"reason":"bad range","suggested_reply":"send"}', { name: 'Sample lead', email: 'lead@example.com' }),
  run('{"score":8,"reason":"missing email","suggested_reply":"send"}', { name: 'Sample lead' })
]) {
  assert.strictEqual(candidate.score, 0);
  assert.strictEqual(candidate.qualification_valid, false);
  assert.strictEqual(candidate.needs_review, true);
  assert.strictEqual(candidate.suggested_reply, '');
}

console.log('ok, lead and qualification fallbacks behave as documented');
