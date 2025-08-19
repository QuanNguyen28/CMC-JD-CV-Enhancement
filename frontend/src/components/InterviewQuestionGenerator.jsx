// src/components/InterviewQuestionGenerator.jsx
import React, { useState } from 'react'
import api from '../api'
import NeumorphicCard from './NeumorphicCard'

export default function InterviewQuestionGenerator({ seed, jdId, meta }) {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    try {
      const payload = {
        jd_id: jdId || 0,
        title: meta.title,
        level: meta.level,
        department: meta.department,
        focus: seed ? seed.split(/\n+/).filter(Boolean) : [],
        count: 8,
        mix: ["technical","behavioral","situational"],
        language: "vi"
      }
      const res = await api.post('/v1/interview/generate', payload)
      setQuestions(res.data?.questions || [])
    } catch (e) {
      setQuestions([])
    } finally { setLoading(false) }
  }

  return (
    <NeumorphicCard>
      <div className="flex items-center justify-between mb-2">
        <div className="font-medium">Interview Questions</div>
        <button onClick={generate} className="btn-ghost">Generate</button>
      </div>
      {loading && <div className="text-sm text-gray-600">Generating…</div>}
      <ol className="list-decimal pl-5 space-y-2">
        {questions.map((q, i) => (
          <li key={i}>
            <div className="font-medium">[{q.type?.toUpperCase()}] {q.question}</div>
            <div className="text-xs text-gray-600">Competency: {q.competency} · Difficulty: {q.difficulty}</div>
            {q.rubric && <div className="text-sm mt-1 whitespace-pre-line">{q.rubric}</div>}
          </li>
        ))}
      </ol>
      {!questions.length && <div className="text-sm text-gray-500">No questions yet.</div>}
    </NeumorphicCard>
  )
}