<!-- <template>
  <v-container>
    <h3>Upload Documents</h3>
    <v-file-input label="PAN Card" v-model="pan"></v-file-input>
    <v-file-input label="Aadhaar Card" v-model="aadhaar"></v-file-input>
    <v-file-input label="Photograph" v-model="photo"></v-file-input>
    <v-btn color="primary" @click="uploadDocuments">Upload</v-btn>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      pan: null,
      aadhaar: null,
      photo: null
    }
  },
  methods: {
    async uploadDocuments() {
      const formData = new FormData()
      if (this.pan) formData.append('pan', this.pan)
      if (this.aadhaar) formData.append('aadhaar', this.aadhaar)
      if (this.photo) formData.append('photo', this.photo)

      const empId = this.$route.params.id
      try {
        await axios.post(`http://127.0.0.1:5000/api/employees/${empId}/upload`, formData)
        alert('Documents uploaded successfully.')
        setTimeout(() => window.close(), 2000)
      } catch (err) {
        alert('Upload failed.')
      }
    }
  }
}
</script> -->


<template>
  <v-container>
    <h3>Upload Documents & Enter Details</h3>

    <!-- Manual fields -->
    <v-text-field
      label="Contact Number"
      v-model="contact_number"
      type="tel"
      required
    ></v-text-field>

    <v-text-field
      label="Contact Address"
      v-model="contact_address"
      required
    ></v-text-field>

    <!-- File Upload Fields -->
    <v-file-input
      label="PAN Card"
      v-model="pan"
      accept=".jpg,.jpeg,.png,.pdf"
      prepend-icon="mdi-card-account-details"
    ></v-file-input>

    <v-file-input
      label="Aadhaar Card"
      v-model="aadhaar"
      accept=".jpg,.jpeg,.png,.pdf"
      prepend-icon="mdi-id-card"
    ></v-file-input>

    <v-file-input
      label="Photograph"
      v-model="photo"
      accept=".jpg,.jpeg,.png"
      prepend-icon="mdi-camera"
    ></v-file-input>

    <!-- Upload Button -->
    <v-btn color="primary" class="mt-4" @click="uploadDocuments">
      Upload
    </v-btn>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      contact_number: '',
      contact_address: '',
      pan: null,
      aadhaar: null,
      photo: null
    }
  },
  methods: {
    async uploadDocuments() {
      if (!this.contact_number || !this.contact_address) {
        alert('Please fill in contact details.')
        return
      }

      const formData = new FormData()
      formData.append('contact_number', this.contact_number)
      formData.append('contact_address', this.contact_address)

      if (this.pan) formData.append('pan', this.pan)
      if (this.aadhaar) formData.append('aadhaar', this.aadhaar)
      if (this.photo) formData.append('photo', this.photo)

      const empId = this.$route.params.id
      try {
        await axios.post(
          `http://127.0.0.1:5000/api/employees/${empId}/upload`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
        alert('Documents uploaded and details saved successfully.')
        setTimeout(() => window.close(), 2000)
      } catch (err) {
        console.error(err)
        alert('Upload failed.')
      }
    }
  }
}
</script>
