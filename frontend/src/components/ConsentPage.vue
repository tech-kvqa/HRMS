<!-- <template>
  <v-container>
    <h3>Consent Form</h3>
    <p>By clicking submit, you provide consent for your data to be used as per company policies.</p>
    <v-btn color="primary" @click="submitConsent">Submit Consent</v-btn>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  methods: {
    async submitConsent() {
      const empId = this.$route.params.id
      try {
        await axios.post(`http://127.0.0.1:5000/api/employees/${empId}/consent`)
        alert('Consent submitted successfully. You may close this window.')
        window.close()
      } catch (error) {
        alert('Error submitting consent.')
      }
    }
  }
}
</script> -->



<template>
  <v-container>
    <h3>Consent Form</h3>
    <p>By clicking submit, you provide consent for your data to be used as per company policies.</p>
    <v-btn color="primary" @click="submitConsent">Submit Consent</v-btn>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  methods: {
    async submitConsent() {
      const empId = this.$route.params.id
      try {
        await axios.post(
          // `http://127.0.0.1:5000/api/employees/${empId}/consent`,
          `https://hrms-ocfa.onrender.com/api/employees/${empId}/consent`,
          { accepted: true }, // Send JSON
          { headers: { 'Content-Type': 'application/json' } } // Set header
        )
        alert('Consent submitted successfully. You may close this window.')
        window.close()
      } catch (error) {
        console.error(error)
        alert('Error submitting consent.')
      }
    }
  }
}
</script>
