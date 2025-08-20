<!-- <template>
  <v-data-table :headers="headers" :items="employees" class="mt-5">
    <template v-slot:item.actions="{ item }">
      <v-btn icon :href="`http://127.0.0.1:5000/consent/${item.id}`" target="_blank">
        <v-icon>mdi-eye</v-icon>
      </v-btn>
    </template>
  </v-data-table>
</template>

<script>
export default {
  props: ['employees'],
  data() {
    return {
      headers: [
        { title: 'Name', value: 'name' },
        { title: 'Email', value: 'email' },
        { title: 'Department', value: 'department' },
        { title: 'Designation', value: 'designation' },
        { title: 'Consent', value: 'consent_status' },
        { title: 'Actions', value: 'actions', sortable: false }
      ]
    }
  }
}
</script> -->


<!-- <template>
  <div>
    <v-data-table :headers="headers" :items="employees" class="mt-5">
      <template v-slot:item.actions="{ item }">
        <v-btn icon :href="`http://127.0.0.1:5000/consent/${item.id}`" target="_blank">
          <v-icon>mdi-eye</v-icon>
        </v-btn>

        <v-btn icon @click="previewDocument(item.id, 'aadhaar')">
          <v-icon>mdi-file-eye</v-icon>
        </v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="previewDialog" max-width="800px">
      <v-card>
        <v-card-title>Document Preview</v-card-title>
        <v-card-text>
          <div v-if="previewMime.startsWith('image/')">
            <img :src="previewUrl" style="max-width: 100%;" />
          </div>
          <div v-else-if="previewMime === 'application/pdf'">
            <iframe :src="previewUrl" width="100%" height="600px"></iframe>
          </div>
          <div v-else>
            Unsupported file type
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: ['employees'],
  data() {
    return {
      headers: [
        { title: 'Name', value: 'name' },
        { title: 'Email', value: 'email' },
        { title: 'Department', value: 'department' },
        { title: 'Designation', value: 'designation' },
        { title: 'Consent', value: 'consent_status' },
        { title: 'Actions', value: 'actions', sortable: false }
      ],
      previewDialog: false,
      // previewContent: { type: '', data: '' }
      previewUrl: '',
      previewMime: ''
    }
  },
  methods: {
    async previewDocument(employeeId, docType) {
      try {
        const res = await fetch(`http://127.0.0.1:5000/api/employees/${employeeId}/preview/${docType}`);
        const data = await res.json();

        if (data.file_base64) {
          this.previewMime = data.mime_type;
          this.previewUrl = `data:${data.mime_type};base64,${data.file_base64}`;
          this.previewDialog = true;
        } else {
          alert(data.error || 'No file available');
        }
      } catch (err) {
        console.error(err);
        alert('Error loading document');
      }
    }
  }
}
</script> -->


<template>
  <v-data-table :headers="headers" :items="employees" class="mt-5">
    <template v-slot:item.actions="{ item }">
      <v-btn icon @click="showEmployeeInfo(item.id)">
        <v-icon>mdi-eye</v-icon>
      </v-btn>
    </template>
  </v-data-table>

  <!-- Employee Info Dialog -->
  <v-dialog v-model="infoDialog" max-width="600px">
    <v-card>
      <v-card-title>Employee Information</v-card-title>
      <v-card-text>
        <div><strong>Name:</strong> {{ selectedEmployee.name }}</div>
        <div><strong>Email:</strong> {{ selectedEmployee.email }}</div>
        <div><strong>Department:</strong> {{ selectedEmployee.department }}</div>
        <div><strong>Designation:</strong> {{ selectedEmployee.designation }}</div>
        <div><strong>PAN:</strong> {{ selectedEmployee.pan_number || 'N/A' }}</div>
        <div><strong>Aadhaar:</strong> {{ selectedEmployee.aadhaar_number || 'N/A' }}</div>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="openDocSelector">Preview Documents</v-btn>
        <v-btn text @click="infoDialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Document Selector Dialog -->
  <v-dialog v-model="docSelectorDialog" max-width="400px">
    <v-card>
      <v-card-title>Select Document to Preview</v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item v-for="doc in availableDocs" :key="doc.type" @click="previewDocument(selectedEmployee.id, doc.type)">
            <v-list-item-title>{{ doc.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="docSelectorDialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Document Preview Dialog -->
  <v-dialog v-model="previewDialog" max-width="800px">
    <v-card>
      <v-card-title>Document Preview</v-card-title>
      <v-card-text>
        <div v-if="previewMime.startsWith('image/')">
          <img :src="previewUrl" style="max-width: 100%;" />
        </div>
        <div v-else-if="previewMime === 'application/pdf'">
          <iframe :src="previewUrl" width="100%" height="600px"></iframe>
        </div>
        <div v-else>
          Unsupported file type
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: ['employees'],
  data() {
    return {
      headers: [
        { title: 'Name', value: 'name' },
        { title: 'Email', value: 'email' },
        { title: 'Department', value: 'department' },
        { title: 'Designation', value: 'designation' },
        { title: 'Consent', value: 'status' },
        { title: 'PAN', value: 'pan_number'},
        { title: 'Aadhaar', value: 'aadhaar_number'},
        { title: 'Contact Number', value: 'contact_number'},
        { title: 'Actions', value: 'actions', sortable: false }
      ],
      selectedEmployee: {},
      infoDialog: false,
      docSelectorDialog: false,
      previewDialog: false,
      previewUrl: '',
      previewMime: '',
      availableDocs: [
        { type: 'photo', label: 'Photograph' },
        { type: 'pan', label: 'PAN Card' },
        { type: 'aadhaar', label: 'Aadhaar Card' },
        { type: 'nda', label: 'NDA' },
        { type: 'offer_letter', label: 'Offer Letter' }
      ]
    }
  },
  methods: {
    async showEmployeeInfo(id) {
      try {
        // const res = await fetch(`http://127.0.0.1:5000/api/employees/${id}/info`);
        const res = await fetch(`https://hrms-4jys.onrender.com/api/employees/${id}/info`);
        const data = await res.json();
        this.selectedEmployee = data;
        this.infoDialog = true;
      } catch (err) {
        console.error(err);
      }
    },
    openDocSelector() {
      this.infoDialog = false;
      this.docSelectorDialog = true;
    },
    async previewDocument(employeeId, docType) {
      this.docSelectorDialog = false;
      try {
        // const res = await fetch(`http://127.0.0.1:5000/api/employees/${employeeId}/preview/${docType}`);
        const res = await fetch(`https://hrms-4jys.onrender.com/api/employees/${employeeId}/preview/${docType}`);
        const data = await res.json();

        if (data.file_base64) {
          this.previewMime = data.mime_type;
          this.previewUrl = `data:${data.mime_type};base64,${data.file_base64}`;
          this.previewDialog = true;
        } else {
          alert(data.error || 'No file available');
        }
      } catch (err) {
        console.error(err);
      }
    }
  }
}
</script>
