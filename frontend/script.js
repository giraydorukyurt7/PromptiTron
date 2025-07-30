document.getElementById("transcript-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = document.getElementById("yturl").value;
  const status = document.getElementById("status");
  const transcriptOutput = document.getElementById("transcript-output");
  const summaryOutput = document.getElementById("summary-output");

  status.textContent = "\u23f3 Transkript al\u0131n\u0131yor...";
  transcriptOutput.textContent = "";
  summaryOutput.textContent = "";

  try {
    const downloadRes = await fetch("/task?task_name=download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const { result: audioPath } = await downloadRes.json();

    const transcribeRes = await fetch("/task?task_name=transcribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audio_path: audioPath })
    });
    const { result: transcript } = await transcribeRes.json();

    status.textContent = "\u2705 Transkript ba\u015far\u0131yla al\u0131nd\u0131.";
    transcriptOutput.textContent = transcript;
    window.currentTranscript = transcript;
  } catch (err) {
    status.textContent = "\u274c Hata olu\u015ftu.";
    console.error(err);
  }
});

const buttonTaskMap = {
  "\ud83d\udcdd \u00d6zetle": "summarize",
  "\ud83c\udf10 WorldCloud Olu\u015ftur": "worldcloud",
  "\ud83d\udcc6 \u00c7al\u0131\u015fma Plan\u0131": "studyplan",
  "\ud83e\udde0 Ak\u0131l Haritas\u0131": "mindmap",
  "\u2753 Zor Sorular \u00dcret": "quiz",
  "\ud83d\udc83 Haf\u0131za Kartlar\u0131": "flashcards",
  "\ud83d\udcda \u00d6nemli Kavramlar": "concepts",
  "\ud83d\udd17 Kaynak \u00d6ner": "resources",
  "\ud83e\uddea S\u0131nav Sim\u00fclasyonu": "exam_simulation",
  "\ud83d\udcac Kritik C\u00fcmleler": "search_similar",
  "\ud83d\udd0d Sorular\u0131 Grupla": "group_questions",
  "\ud83d\udcdc PDF Olarak Kaydet": "export_pdf",
  "\ud83d\udd17 Payla\u015f\u0131labilir Link": "share_link",
  "\ud83c\udfaf Kavram Testi Olu\u015ftur": "concept_quiz"
};

document.querySelectorAll(".action-btn").forEach(button => {
  button.addEventListener("click", async () => {
    const status = document.getElementById("status");
    const output = document.getElementById("summary-output");
    const label = button.innerText;
    const taskName = buttonTaskMap[label];

    if (!window.currentTranscript && taskName !== "export_pdf") {
      status.textContent = "\u2139\ufe0f L\u00fctfen \u00f6nce transkript al\u0131n.";
      return;
    }

    status.textContent = `\u23f3 ${label} ba\u015flat\u0131l\u0131yor...`;
    output.textContent = "";

    try {
      if (taskName === "export_pdf") {
        const pdfResponse = await fetch("/task?task_name=export_pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sections: {
              "Transkript": window.currentTranscript || "",
              "\u00d6zet": document.getElementById("summary-output").textContent || ""
            }
          })
        });
        const { result: pdfPath } = await pdfResponse.json();
        const filename = pdfPath.split("/").pop();

        const link = document.createElement("a");
        link.href = `/download?file=${encodeURIComponent(pdfPath)}`;
        link.download = filename;
        link.click();
        status.textContent = `\u2705 PDF indirildi: ${filename}`;
        return;
      }

      if (taskName === "search_similar") {
        await fetch("/task?task_name=build_vector_store", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: window.currentTranscript })
        });

        const result = await fetch("/task?task_name=search_similar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: "kritik bilgi, tan\u0131m ve \u00f6zet" })
        });

        const { result: similarText } = await result.json();
        output.textContent = similarText.join ? similarText.join("\n\n") : similarText;
        status.textContent = `\u2705 ${label} tamamland\u0131.`;
        return;
      }

      const response = await fetch(`/task?task_name=${taskName}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: window.currentTranscript })
      });

      const { result } = await response.json();
      output.textContent = result;
      status.textContent = `\u2705 ${label} tamamland\u0131.`;
    } catch (err) {
      console.error(err);
      status.textContent = `\u274c ${label} s\u0131ras\u0131nda hata.`;
    }
  });
});