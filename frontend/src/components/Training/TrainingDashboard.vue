<template>
  <v-container>
    <!-- Question Modal -->

    <v-btn color="secondary" @click="openQuestionModal">Manage Questions</v-btn>
    <v-dialog v-model="showQuestionModal" max-width="800">
      <v-card>
        <v-card-title>
          {{ isEditing ? 'Edit Question' : 'Add Question' }}
          <v-spacer></v-spacer>
          <v-btn icon @click="closeQuestionModal">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>
          <v-form @submit.prevent="isEditing ? updateQuestion() : addQuestion()">
            <v-text-field
              v-model="question.question_text"
              label="Question Text"
              required
            />

            <div v-for="(option, index) in question.options" :key="index" class="d-flex align-center mb-2">
              <v-text-field
                v-model="question.options[index]"
                label="Option"
                class="flex-grow-1"
                required
              />
              <v-btn icon color="red" @click="deleteOption(index)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>

            <v-btn variant="outlined" color="primary" @click="addOption">Add Option</v-btn>

            <v-select
              v-model="question.answer"
              :items="question.options"
              label="Select Correct Answer"
              required
            />

            <div class="d-flex justify-end mt-4">
              <v-btn type="submit" color="success" class="mr-2">{{ isEditing ? 'Update' : 'Add' }}</v-btn>
              <v-btn variant="outlined" @click="cancel">Cancel</v-btn>
            </div>
          </v-form>

          <!-- Questions List -->
          <v-divider class="my-4"></v-divider>
          <h3>Questions List</h3>
          <v-data-table :items="questions" :headers="questionHeaders">
            <template #item.actions="{ item }">
              <v-btn size="small" color="info" @click="editQuestion(item)">Edit</v-btn>
              <v-btn size="small" color="error" @click="deleteQuestion(item.id)">Delete</v-btn>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Department Selector & Upload -->
    <v-card class="mt-6 pa-4">
      <v-select
        v-model="selectedDepartment"
        :items="departments"
        label="Select Department"
        outlined
        dense
      />

      <v-file-input
        v-model="file"
        label="Upload Colleagues Data (.xlsx)"
        accept=".xlsx"
        outlined
      />

      <v-btn color="primary" class="mr-2" @click="uploadColleaguesData">Upload</v-btn>
      <v-btn color="error" @click="deleteColleaguesData">Delete</v-btn>
    </v-card>

    <!-- Action Buttons -->
    <v-card class="mt-6 pa-4 d-flex flex-wrap gap-2">
      <v-btn color="primary" @click="sendPhishingEmails">Send Phishing Email</v-btn>
      <v-btn color="secondary" @click="downloadReport">Download Performance Report</v-btn>
      <v-btn color="info" @click="downloadReportPdf">Download Complete Report</v-btn>
      <v-btn color="warning" @click="emailedCandidatesReport">Generate Emailed Candidates Report</v-btn>
      <v-btn color="success" @click="sendReminder">Send Reminder</v-btn>
      <v-btn color="purple" class="mb-4" @click="downloadTrainingSessionsCsv">Download Training Sessions CSV</v-btn>
    </v-card>

    <!-- Candidate Reports -->
    <v-card class="mt-6 pa-4">
      <h2>Candidate Reports</h2>
      <v-data-table :items="reports" :headers="reportHeaders">
        <template #item.clicked="{ item }">
          {{ item.clicked ? "Yes" : "No" }}
        </template>
        <template v-slot:item.colleague_id="{ item }">
            {{ getColleagueName(item.colleague_id) }}
        </template>
        <template #item.answered="{ item }">
          {{ item.answered ? "Yes" : "No" }}
        </template>
        <template #item.correctAnswers="{ item }">
          {{ calculateCorrectAnswers(item.score) }}/{{ item.answers.length }}
        </template>
        <template #item.status="{ item }">
          <v-chip :color="item.status === 'Completed' ? 'green' : 'orange'">
            {{ item.status }}
          </v-chip>
        </template>
        <template #item.certificate="{ item }">
          <v-btn
            v-if="item.status === 'Completed' && item.score >= 70"
            @click="downloadCertificate(item.colleague_id)"
            size="small"
            color="success"
          >
            Download
          </v-btn>
          <span v-else>-</span>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  name: "Dashboard",
  data() {
    return {
        reports: [],
        questions: [],
        colleagues: [],
        pollingInterval: null,
        isGenerating: false,
        file: null,
        showQuestionModal: false,
        selectedDepartment: '',
        isEditing: false,
        status: "Pending",
        question: {
            id: null,
            question_text: '',
            options: ['', ''],
            answer: ''
    },

      departments: [
        "Leadership",
        "Developer and Product Development",
        "Sales and Marketing, Finance, Admin",
        "HR, Information Security, Training and TMG",
      ],

      questionHeaders: [
        { title: "ID", value: "id" },
        { title: "Question", value: "question_title" },
        { title: "Options", value: "options" },
        { title: "Answer", value: "answer" },
        { title: "Actions", value: "actions", sortable: false },
      ],

      reportHeaders: [
        { title: "ID", value: "id" },
        { title: "Colleague", value: "colleague_id" },
        { title: "Link Clicked", value: "clicked" },
        { title: "Training Completed", value: "answered" },
        { title: "Correct Answers", value: "correctAnswers" },
        { title: "Score", value: "score" },
        { title: "Status", value: "status" },
        { title: "Training Date", value: "completion_date" },
        { title: "Certificate", value: "certificate", sortable: false },
      ],
    };
  },
  methods: {
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        // return date.toLocaleDateString('en-GB'); // Format as dd-mm-yyyy
        // return `${date.getDate().toString().padStart(2, '0')}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getFullYear()}`;

        const day = date.getUTCDate().toString().padStart(2, '0');
        const month = (date.getUTCMonth() + 1).toString().padStart(2, '0'); // Months are 0-based
        const year = date.getUTCFullYear();
        return `${day}-${month}-${year}`; // Format as dd-mm-yyyy
    },

    async sendPhishingEmails() {
        if (!this.selectedDepartment) {
            alert("Please select a department before sending emails.");
            return;
        }

        try {
            // const response = await fetch('http://127.0.0.1:5000/api/send_email', {
            const response = await fetch('https://hrms-4jys.onrender.com/api/send_email', {
            // const response = await fetch('https://phishing-application-demo.onrender.com/send_email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ department: this.selectedDepartment })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            this.message = data.message;
            alert("Email Send to Candidates")
        } catch (error) {
            console.error('Failed to send emails:', error);
            this.message = 'Error sending emails. Please try again.';
        }
    },
    async downloadReport() {
        // const response = await fetch('http://127.0.0.1:5000/api/generate_reports');
        const response = await fetch('https://hrms-4jys.onrender.com/api/generate_reports');
        // const response = await fetch('http://35.182.29.153/api/generate_reports');
        // const response = await fetch('https://phishing-application-demo.onrender.com/generate_reports');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'candidate_reports.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    },

    async fetchReports() {
        try {
            // const response = await fetch('http://127.0.0.1:5000/api/get_all_reports');
            const response = await fetch('https://hrms-4jys.onrender.com/api/get_all_reports');
            // const response = await fetch('http://35.182.29.153/api/get_all_reports');
            // const response = await fetch('https://phishing-application-demo.onrender.com/get_all_reports');
            if (!response.ok) {
                throw new Error('Failed to fetch reports');
            }
            const data = await response.json();
            this.reports = data.reports;  // Assuming 'reports' is the key in the response
        } catch (error) {
            console.error('Error fetching reports:', error);
        }
    },
    async fetchQuestions() {
        try {
            // const response = await fetch('http://127.0.0.1:5000/api/questions');
            const response = await fetch('https://hrms-4jys.onrender.com/api/questions');
            // const response = await fetch('http://35.182.29.153/api/questions');
            // const response = await fetch('https://phishing-application-demo.onrender.com/questions');
            const data = await response.json();
            this.questions = data;
        } catch (error) {
            console.error('Failed to fetch questions:', error);
        }
    },

    async fetchColleagues() {
        try {
            // const response = await fetch('http://127.0.0.1:5000/api/users');
            const response = await fetch('https://hrms-4jys.onrender.com/api/users');
            // const response = await fetch('http://35.182.29.153/api/users');
            // const response = await fetch('https://phishing-application-demo.onrender.com/users');
            const data = await response.json();
            this.colleagues = data;
        } catch (error) {
            console.error('Failed to fetch colleagues:', error);
        }
    },

    getColleagueName(colleagueId) {
        const colleague = this.colleagues.find(c => c.id === colleagueId);
        return colleague ? colleague.name : 'Unknown';
    },

    calculateCorrectAnswers(score) {
        if (typeof score !== 'number' || isNaN(score)) {
            return 0; // If score is not a valid number, return 0
        }

        // Calculate the correct number of answers by dividing the score by 10
        const correctAnswers = Math.round(score / 10);

        return correctAnswers;
    },

    calculateScoreOutOf100(answers) {
        const correctAnswers = this.calculateCorrectAnswers(answers);
        const totalQuestions = this.questions.length;
        const scoreOutOf100 = (correctAnswers / totalQuestions) * 100;
        return scoreOutOf100.toFixed(2);
    },

    isCorrect(questionIndex, answer) {
        const question = this.questions[questionIndex];
        return question && question.answer === answer;
    },

    async emailedCandidatesReport() {
        if (this.isGenerating) return;
        this.isGenerating = true;
        this.stopPolling();

        try {
            // const response = await fetch(`http://127.0.0.1:5000/api/generate_emailed_candidates_report`, {
            const response = await fetch(`https://hrms-4jys.onrender.com/api/generate_emailed_candidates_report`, {
            // const response = await fetch(`http://35.182.29.153/api/generate_emailed_candidates_report`, {
            // const response = await fetch(`https://phishing-application-demo.onrender.com/generate_emailed_candidates_report`, {
                method: 'GET'
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", "emailed_candidates_report.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error || response.statusText}`);
            }
        } catch (error) {
            console.error("Error generating report:", error);
            alert("An error occurred while generating the report.");
        } finally {
            this.isGenerating = false;
            this.startPolling();
        }
    },

    startPolling() {
        this.fetchReports();
        this.pollingInterval = setInterval(async () => {
            if (!this.isGenerating) {
                await this.fetchReports();
            }
        }, 5000);
    },

    async uploadColleaguesData() {
        if (!this.file) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append('file', this.file);

        try {
            // const response = await fetch('http://127.0.0.1:5000/api/upload_colleagues_data', {
            const response = await fetch('https://hrms-4jys.onrender.com/api/upload_colleagues_data', {
            // const response = await fetch('http://35.182.29.153/api/upload_colleagues_data', {
            // const response = await fetch('https://phishing-application-demo.onrender.com/upload_colleagues_data', {
            method: 'POST',
            body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            alert("Colleagues data updated successfully!");
        } catch (error) {
            console.error("Error uploading data:", error);
            alert("Failed to upload data. Please try again.");
        }
    },

    handleFileUpload(event) {
        this.file = event.target.files[0];
    },

    stopPolling() {
        clearInterval(this.pollingInterval);
    },

    openQuestionModal() {
        this.showQuestionModal = true;
        this.fetchQuestions();
    },

    closeQuestionModal() {
        this.showQuestionModal = false;
        this.resetQuestionForm();
    },

    resetQuestionForm() {
        this.isEditing = false;
        this.question = {
            id: null,
            question_text: '',
            options: ['', ''],
            answer: ''
        };
    },

    async fetchQuestions() {
        try {
            // const response = await fetch('http://127.0.0.1:5000/api/questions');
            const response = await fetch('https://hrms-4jys.onrender.com/api/questions');
            // const response = await fetch('http://35.182.29.153/api/questions');
            // const response = await fetch('https://phishing-application-demo.onrender.com/questions');
            const data = await response.json();
            this.questions = data;
        } catch (error) {
            console.error('Failed to fetch questions:', error);
        }
    },

    async addQuestion() {
        // const response = await fetch('http://127.0.0.1:5000/api/questions', {
        const response = await fetch('https://hrms-4jys.onrender.com/api/questions', {
        // const response = await fetch('http://35.182.29.153/api/questions', {
        // const response = await fetch('https://phishing-application-demo.onrender.com/questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.question)
        });
        await response.json();
        this.fetchQuestions();
        this.resetForm();
    },

    async editQuestion(question) {
        this.currentQuestionId = question.id;
        this.question = { ...question };

        if (!Array.isArray(this.question.options)) {
            this.question.options = [];
        }

        this.isEditing = true;
        this.showQuestionForm = true;
    },

    async updateQuestion() {
        if (!this.currentQuestionId) {
            alert('No question selected for updating.');
            return;
        }

        // const response = await fetch(`http://127.0.0.1:5000/api/questions/${this.currentQuestionId}`, {
        const response = await fetch(`https://hrms-4jys.onrender.com/api/questions/${this.currentQuestionId}`, {
        // const response = await fetch(`http://35.182.29.153/api/questions/${this.currentQuestionId}`, {
        // const response = await fetch(`https://phishing-application-demo.onrender.com/questions/${this.currentQuestionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.question)
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error updating question:', errorData);
            alert(`Error: ${errorData.error || 'Something went wrong!'}`);
            return;
        }

        const data = await response.json();
        console.log('Success:', data.message);
        this.fetchQuestions();
        this.resetForm();
    },

    async deleteQuestion(id) {
        // await fetch(`http://127.0.0.1:5000/api/questions/${id}`, {
        await fetch(`https://hrms-4jys.onrender.com/api/questions/${id}`, {
        // await fetch(`http://35.182.29.153/api/questions/${id}`, {
        // await fetch(`https://phishing-application-demo.onrender.com/questions/${id}`, {
            method: 'DELETE'
        });
        this.fetchQuestions();
    },

    resetForm() {
        this.question = {
            question_text: '',
            options: ['', ''],
            answer: ''
        };
        this.isEditing = false;
        this.currentQuestionId = null;
    },

    addOption() {
        if (Array.isArray(this.question.options)) {
            if (this.question.options.length < 4) {
                this.question.options.push('');
            } else {
                alert('You can only add up to 4 options.');
            }
        } else {
            console.error("Options is not defined or is not an array");
        }
    },

    deleteOption(index) {
        if (this.question.options.length > 2) {
            this.question.options.splice(index, 1);
        } else {
            alert('You must have at least 2 options.');
        }
    },

    cancel() {
        this.resetQuestionForm();
    },

    async sendReminder() {
        try {
            const pendingReports = this.reports.filter(report => report.status === 'Pending');
            for (const report of pendingReports) {
                // await fetch(`http://127.0.0.1:5000/api/send_reminder/${report.id}`, {
                await fetch(`https://hrms-4jys.onrender.com/api/send_reminder/${report.id}`, {
                // await fetch(`http://35.182.29.153/api/send_reminder/${report.id}`, {
                // await fetch(`https://phishing-application-demo.onrender.com/send_reminder/${report.id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
            }
            alert('Reminders sent to all pending reports.');
        } catch (error) {
            console.error('Error sending reminders:', error);
            alert('Failed to send reminders. Please try again.');
        }
    },

    async deleteColleaguesData() {
        if (!confirm("Are you sure you want to delete all colleagues? This action cannot be undone.")) {
            return;
        }

        try {
            // const response = await fetch('http://127.0.0.1:5000/api/delete_colleagues_data', {
            const response = await fetch('https://hrms-4jys.onrender.com/api/delete_colleagues_data', {
            // const response = await fetch('http://35.182.29.153/api/delete_colleagues_data', {
            // const response = await fetch('https://phishing-application-demo.onrender.com/delete_colleagues_data', {
                method: 'DELETE'
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message);
                // Optionally, clear the colleagues list in the frontend
                this.colleagues = [];
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Failed to delete colleagues.");
            }
        } catch (error) {
            console.error("Error deleting colleagues:", error);
            alert("An error occurred while deleting colleagues.");
        }
    },

    async downloadCertificate(colleagueId) {
        try {
            // const response = await fetch(`http://127.0.0.1:5000/api/download-certificate/${colleagueId}`, {
            const response = await fetch(`https://hrms-4jys.onrender.com/api/download-certificate/${colleagueId}`, {
            // const response = await fetch(`http://35.182.29.153/api/download-certificate/${colleagueId}`, {
            // const response = await fetch(`https://phishing-application-demo.onrender.com/download-certificate/${colleagueId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/pdf',
                },
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `Certificate_${colleagueId}.pdf`);
                document.body.appendChild(link);
                link.click();
                link.remove();
            } else {
                const errorData = await response.json();
                alert(errorData.error || "Failed to download the certificate.");
            }
        } catch (error) {
            console.error("Error downloading certificate:", error);
            alert("An error occurred while downloading the certificate.");
        }
    },

    async downloadReportPdf() {
        try {
            // const response = await fetch('http://127.0.0.1:5000/api/generate_reports_pdf');
            const response = await fetch('https://hrms-4jys.onrender.com/api/generate_reports_pdf');
            // const response = await fetch('http://35.182.29.153/api/generate_reports_pdf');
            if (!response.ok) throw new Error('Failed to fetch PDF report');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.href = url;
            link.download = 'Phishing_Simulation_Report.pdf';
            link.click();

            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading report:', error);
            alert('Could not download PDF report at this time.');
        }
    },

    async downloadTrainingSessionsCsv() {
        try {
            // const response = await fetch("http://127.0.0.1:5000/api/training-sessions/csv");
            const response = await fetch("https://hrms-4jys.onrender.com/api/training-sessions/csv");
            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", "training_sessions.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error("Error downloading training sessions CSV:", error);
        }
    }
  },
  mounted() {
    this.fetchQuestions();
    this.fetchReports();
    this.fetchColleagues();
    this.startPolling();
  },
};
</script>

<style scoped>
.logo {
  height: 50px;
}
</style>
