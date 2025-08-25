import { useState } from 'react';
import { InterviewAPI } from '../api';

export default function InterviewPage() {
  const [payload, setPayload] = useState({
    jd_id: 0,
    title: '',
    level: '',
    department: '',
    focus: [],
    count: 8,
    mix: ['technical', 'behavioral', 'situational'],
    language: 'vi',
  });

  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [questions, setQuestions] = useState([]);

  const toggleFocus = (tag) => {
    setPayload(p => {
      const has = p.focus.includes(tag);
      return { ...p, focus: has ? p.focus.filter(t => t !== tag) : [...p.focus, tag] };
    });
  };

  const run = async () => {
    setBusy(true); setErr('');
    try {
      const data = await InterviewAPI.generate(payload);
      setQuestions(data?.questions || []);
    } catch (e) {
      setErr(e?.response?.data?.detail || String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="bg-white border rounded-xl p-4 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          {['title','level','department'].map((k) => (
            <div key={k}>
              <label className="block text-sm mb-1 capitalize">{k}</label>
              <input
                className="w-full border rounded-md px-3 py-2"
                value={payload[k]}
                onChange={(e) => setPayload({ ...payload, [k]: e.target.value })}
              />
            </div>
          ))}
          <div>
            <label className="block text-sm mb-1">Count</label>
            <input
              type="number"
              className="w-full border rounded-md px-3 py-2"
              value={payload.count}
              onChange={(e) => setPayload({ ...payload, count: Number(e.target.value) || 8 })}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm mb-1">Focus</label>
          <div className="flex flex-wrap gap-2">
            {['system design','python','sql','communication','ownership'].map(f => (
              <button
                key={f}
                onClick={() => toggleFocus(f)}
                className={`px-3 py-1.5 rounded-md border ${payload.focus.includes(f) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white'}`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm mb-1">Mix</label>
          <div className="flex gap-2">
            {['technical','behavioral','situational'].map(t => (
              <label key={t} className="text-sm flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={payload.mix.includes(t)}
                  onChange={() =>
                    setPayload(p => {
                      const has = p.mix.includes(t);
                      return { ...p, mix: has ? p.mix.filter(x=>x!==t) : [...p.mix, t] };
                    })
                  }
                />
                {t}
              </label>
            ))}
          </div>
        </div>

        <button
          onClick={run}
          disabled={busy}
          className="px-4 py-2 rounded-md bg-blue-600 text-white"
        >
          {busy ? 'Generating…' : 'Generate Questions'}
        </button>

        {err && <div className="text-sm text-red-600">{err}</div>}
      </div>

      <div className="bg-white border rounded-xl p-4">
        <div className="font-semibold mb-3">Questions</div>
        <ol className="space-y-2 list-decimal list-inside">
          {questions.map((q, i) => (
            <li key={i} className="text-sm">
              <div className="font-medium">{q.question}</div>
              <div className="text-xs text-gray-500">
                {q.type} • {q.competency} • {q.difficulty}
              </div>
              {q.rubric && <div className="text-xs mt-1">{q.rubric}</div>}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}