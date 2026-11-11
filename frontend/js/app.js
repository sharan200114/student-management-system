
// ==========================================
// STUDENT MANAGEMENT SYSTEM
// FRONTEND + FLASK REST API INTEGRATION
// ==========================================

// Flask API base URL
const API_BASE_URL = "http://127.0.0.1:5000/api";

// Student records loaded from MySQL
let students = [];

// HTML elements
const studentForm = document.getElementById("studentForm");
const studentTableBody = document.getElementById("studentTableBody");
const formSection = document.getElementById("registration");

const searchInput = document.getElementById("searchInput");

const addStudentBtn = document.getElementById("addStudentBtn");
const closeFormBtn = document.getElementById("closeFormBtn");



// ==========================================
// API REQUEST HELPER
// ==========================================

async function apiRequest(endpoint, options = {}) {

    const token = sessionStorage.getItem("access_token");

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {

        ...options,

        headers: {
            "Content-Type": "application/json",
            ...options.headers,

            ...(token ? {
                "Authorization": `Bearer ${token}`
            } : {})
        }

    });

    const result = await response.json();

    if (response.status === 401) {

        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("admin");

        window.location.replace("login.html");

        throw new Error("Session expired. Please login again.");

    }

    if (!response.ok || result.success === false) {

        throw new Error(
            result.message || result.msg || "Something went wrong."
        );

    }

    return result;

}


// ==========================================
// SAFE HTML DISPLAY
// ==========================================

function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[character]);

}

// ==========================================
// LOAD STUDENTS FROM DATABASE
// ==========================================

async function loadStudents() {

    studentTableBody.innerHTML = `
        <tr>
            <td colspan="7" class="empty-message">
                Loading students...
            </td>
        </tr>
    `;

    try {

        const result = await apiRequest("/students");

        // Extract student records from API response
        students = Array.isArray(result.data)
            ? result.data
            : [];

        // Update dashboard
        displayStudents();

        updateStatistics();

        console.log("Students loaded successfully:", students);

    } catch (error) {

        console.error("Loading error:", error);

        studentTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-message">
                    ${escapeHTML(error.message)}
                </td>
            </tr>
        `;

    }

}

// ==========================================
// DISPLAY STUDENTS
// ==========================================

function displayStudents(data = students) {

    studentTableBody.innerHTML = "";

    if (data.length === 0) {

        studentTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-message">
                    No students found.
                </td>
            </tr>
        `;

        return;
    }

    data.forEach(student => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${student.id}</td>

            <td>${escapeHTML(student.full_name)}</td>

            <td>${escapeHTML(student.email)}</td>

            <td>${escapeHTML(student.phone)}</td>

            <td>${escapeHTML(student.gender)}</td>

            <td>${escapeHTML(student.course)}</td>

            <td>
                <button
                    class="action-btn edit-btn"
                    data-action="edit"
                    data-id="${student.id}">
                    Edit
                </button>

                <button
                    class="action-btn delete-btn"
                    data-action="delete"
                    data-id="${student.id}">
                    Delete
                </button>
            </td>
        `;

        studentTableBody.appendChild(row);

    });

}


// ==========================================
// UPDATE DASHBOARD STATISTICS
// ==========================================

function updateStatistics() {

    document.getElementById("totalStudents").textContent =
        students.length;

    document.getElementById("maleStudents").textContent =
        students.filter(student =>
            student.gender === "Male"
        ).length;

    document.getElementById("femaleStudents").textContent =
        students.filter(student =>
            student.gender === "Female"
        ).length;

}


// ==========================================
// OPEN REGISTRATION FORM
// ==========================================

addStudentBtn.addEventListener("click", () => {

    studentForm.reset();

    document.getElementById("studentId").value = "";

    document.querySelector(
        "#studentForm button[type='submit']"
    ).textContent = "Save Student";

    formSection.classList.add("show");

    formSection.scrollIntoView({
        behavior: "smooth"
    });

});


// ==========================================
// CLOSE REGISTRATION FORM
// ==========================================

closeFormBtn.addEventListener("click", () => {

    formSection.classList.remove("show");

});


// ==========================================
// ADD OR UPDATE STUDENT
// ==========================================

studentForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const id = document.getElementById("studentId").value;

    // Prepare student data for Flask API
    const student = {

        full_name: document.getElementById("fullName").value.trim(),

        email: document.getElementById("email").value.trim(),

        phone: document.getElementById("phone").value.trim(),

        gender: document.getElementById("gender").value,

        course: document.getElementById("course").value.trim()

    };

    const submitButton = document.querySelector(
        "#studentForm button[type='submit']"
    );

    const originalText = submitButton.textContent;

    submitButton.disabled = true;
    submitButton.textContent = "Saving...";

    try {

        if (id) {

            // UPDATE existing student
            await apiRequest(`/students/${id}`, {
                method: "PUT",
                body: JSON.stringify(student)
            });

            alert("Student updated successfully!");

        } else {

            // CREATE new student
            await apiRequest("/students", {
                method: "POST",
                body: JSON.stringify(student)
            });

            alert("Student registered successfully!");

        }

        studentForm.reset();

        document.getElementById("studentId").value = "";

        formSection.classList.remove("show");

        await loadStudents();

    } catch (error) {

        console.error("Save error:", error);

        alert(error.message);

    } finally {

        submitButton.disabled = false;
        submitButton.textContent = originalText;

    }

});


// ==========================================
// EDIT AND DELETE BUTTON HANDLING
// ==========================================

studentTableBody.addEventListener("click", async (event) => {

    const button = event.target.closest("button[data-action]");

    if (!button) return;

    const id = Number(button.dataset.id);

    const action = button.dataset.action;

    if (action === "edit") {

        editStudent(id);

    } else if (action === "delete") {

        await deleteStudent(id);

    }

});


// ==========================================
// EDIT STUDENT
// ==========================================

function editStudent(id) {

    const student = students.find(
        student => student.id === id
    );

    if (!student) {

        alert("Student not found.");

        return;
    }

    document.getElementById("studentId").value =
        student.id;

    document.getElementById("fullName").value =
        student.full_name;

    document.getElementById("email").value =
        student.email;

    document.getElementById("phone").value =
        student.phone || "";

    document.getElementById("gender").value =
        student.gender;

    document.getElementById("course").value =
        student.course;

    document.querySelector(
        "#studentForm button[type='submit']"
    ).textContent = "Update Student";

    formSection.classList.add("show");

    formSection.scrollIntoView({
        behavior: "smooth"
    });

}


// ==========================================
// DELETE STUDENT
// ==========================================

async function deleteStudent(id) {

    const confirmation = confirm(
        "Are you sure you want to delete this student?"
    );

    if (!confirmation) return;

    try {

        await apiRequest(`/students/${id}`, {
            method: "DELETE"
        });

        alert("Student deleted successfully!");

        await loadStudents();

    } catch (error) {

        console.error("Delete error:", error);

        alert(error.message);

    }

}


// ==========================================
// SEARCH STUDENTS
// ==========================================

searchInput.addEventListener("input", () => {

    const keyword = searchInput.value.toLowerCase().trim();

    const filteredStudents = students.filter(student => {

        return (
            student.full_name.toLowerCase().includes(keyword) ||

            student.email.toLowerCase().includes(keyword) ||

            (student.phone || "").toLowerCase().includes(keyword) ||

            student.course.toLowerCase().includes(keyword)

        );

    });

    displayStudents(filteredStudents);

});


// ==========================================
// INITIAL APPLICATION LOAD
// ==========================================

const accessToken = sessionStorage.getItem("access_token");

if (!accessToken) {

    window.location.replace("login.html");

} else {

    loadStudents();

}

const logoutBtn = document.getElementById("logoutBtn");

logoutBtn.addEventListener("click", () => {

    const confirmation = confirm(
        "Are you sure you want to logout?"
    );

    if (!confirmation) return;

    sessionStorage.removeItem("access_token");

    sessionStorage.removeItem("admin");

    window.location.replace("login.html");

});
