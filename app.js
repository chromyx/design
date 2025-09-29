// Application Data
const userData = {
  "users": [
    {
      "id": 1,
      "username": "admin", 
      "password": "admin123",
      "role": "admin",
      "name": "Administrator",
      "email": "admin@attendix.com",
      "department": "IT",
      "position": "System Administrator"
    },
    {
      "id": 2,
      "username": "hr_manager",
      "password": "hr123", 
      "role": "hr",
      "name": "Sarah Johnson",
      "email": "sarah@attendix.com",
      "department": "Human Resources",
      "position": "HR Manager"
    },
    {
      "id": 3,
      "username": "john_doe",
      "password": "emp123",
      "role": "employee", 
      "name": "John Doe",
      "email": "john@attendix.com",
      "department": "Engineering",
      "position": "Senior Developer"
    },
    {
      "id": 4,
      "username": "alice_smith",
      "password": "emp123",
      "role": "employee",
      "name": "Alice Smith", 
      "email": "alice@attendix.com",
      "department": "Marketing",
      "position": "Marketing Manager"
    },
    {
      "id": 5,
      "username": "bob_wilson",
      "password": "emp123",
      "role": "employee",
      "name": "Bob Wilson",
      "email": "bob@attendix.com", 
      "department": "Sales",
      "position": "Sales Director"
    }
  ],
  "attendance_records": [
    {
      "id": 1,
      "employee_id": 1,
      "employee_name": "Administrator",
      "date": "2024-03-29",
      "clock_in": "08:00",
      "clock_out": "17:00", 
      "status": "Present",
      "hours": "9.0"
    },
    {
      "id": 2,
      "employee_id": 2,
      "employee_name": "Sarah Johnson",
      "date": "2024-03-29",
      "clock_in": "08:30",
      "clock_out": "17:30",
      "status": "Present", 
      "hours": "9.0"
    },
    {
      "id": 3,
      "employee_id": 3,
      "employee_name": "John Doe",
      "date": "2024-03-29", 
      "clock_in": "09:15",
      "clock_out": "18:00",
      "status": "Late",
      "hours": "8.75"
    },
    {
      "id": 4,
      "employee_id": 4,
      "employee_name": "Alice Smith",
      "date": "2024-03-29",
      "clock_in": null,
      "clock_out": null,
      "status": "Absent",
      "hours": "0"
    },
    {
      "id": 5,
      "employee_id": 5,
      "employee_name": "Bob Wilson",
      "date": "2024-03-29",
      "clock_in": "08:45",
      "clock_out": "17:15",
      "status": "Present",
      "hours": "8.5"
    }
  ],
  "leave_requests": [
    {
      "id": 1,
      "employee_id": 3,
      "employee_name": "John Doe",
      "leave_type": "Annual Leave",
      "start_date": "2024-04-01",
      "end_date": "2024-04-03", 
      "days": 3,
      "reason": "Family vacation",
      "status": "Pending",
      "applied_date": "2024-03-25"
    },
    {
      "id": 2,
      "employee_id": 4,
      "employee_name": "Alice Smith",
      "leave_type": "Sick Leave",
      "start_date": "2024-03-29",
      "end_date": "2024-03-29",
      "days": 1, 
      "reason": "Flu symptoms",
      "status": "Approved",
      "applied_date": "2024-03-28"
    },
    {
      "id": 3,
      "employee_id": 5,
      "employee_name": "Bob Wilson",
      "leave_type": "Personal Leave",
      "start_date": "2024-04-05",
      "end_date": "2024-04-05",
      "days": 1,
      "reason": "Personal appointment",
      "status": "Rejected",
      "applied_date": "2024-03-20"
    }
  ],
  "payroll_records": [
    {
      "id": 1,
      "employee_id": 1,
      "employee_name": "Administrator", 
      "month": "March 2024",
      "basic_salary": 8000,
      "allowances": 1000,
      "deductions": 800,
      "net_salary": 8200,
      "status": "Paid"
    },
    {
      "id": 2,
      "employee_id": 3,
      "employee_name": "John Doe",
      "month": "March 2024",
      "basic_salary": 6000,
      "allowances": 500,
      "deductions": 600,
      "net_salary": 5900, 
      "status": "Processing"
    },
    {
      "id": 3,
      "employee_id": 4,
      "employee_name": "Alice Smith",
      "month": "March 2024",
      "basic_salary": 5500,
      "allowances": 400,
      "deductions": 550,
      "net_salary": 5350,
      "status": "Paid"
    }
  ]
};

// Current user session
let currentUser = null;

// Navigation configurations by role
const navigationConfig = {
  admin: [
    { id: 'dashboard', icon: 'bi-speedometer2', title: 'Dashboard' },
    { id: 'employees', icon: 'bi-people', title: 'Employees' },
    { id: 'attendance', icon: 'bi-clock', title: 'Attendance' },
    { id: 'leaves', icon: 'bi-calendar-x', title: 'Leaves' },
    { id: 'payroll', icon: 'bi-currency-dollar', title: 'Payroll' }
  ],
  hr: [
    { id: 'dashboard', icon: 'bi-speedometer2', title: 'Dashboard' },
    { id: 'employees', icon: 'bi-people', title: 'Employees' },
    { id: 'attendance', icon: 'bi-clock', title: 'Attendance' },
    { id: 'leaves', icon: 'bi-calendar-x', title: 'Leaves' },
    { id: 'payroll', icon: 'bi-currency-dollar', title: 'Payroll' }
  ],
  employee: [
    { id: 'dashboard', icon: 'bi-speedometer2', title: 'Dashboard' },
    { id: 'attendance', icon: 'bi-clock', title: 'My Attendance' },
    { id: 'leaves', icon: 'bi-calendar-x', title: 'My Leaves' },
    { id: 'payroll', icon: 'bi-currency-dollar', title: 'My Payroll' },
    { id: 'profile', icon: 'bi-person', title: 'Profile' }
  ]
};

// Utility Functions
function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
}

function getStatusClass(status) {
  const statusMap = {
    'Present': 'success',
    'Late': 'warning', 
    'Absent': 'error',
    'Approved': 'success',
    'Pending': 'warning',
    'Rejected': 'error',
    'Paid': 'success',
    'Processing': 'warning'
  };
  return statusMap[status] || 'info';
}

// Authentication
function initAuth() {
  const loginForm = document.getElementById('loginForm');
  const demoBtns = document.querySelectorAll('.demo-btn');
  
  // Handle demo button clicks
  demoBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const username = btn.dataset.username;
      const password = btn.dataset.password;
      
      document.getElementById('username').value = username;
      document.getElementById('password').value = password;
      
      // Auto-login after a brief moment
      setTimeout(() => {
        handleLogin(username, password);
      }, 300);
    });
  });
  
  // Handle form submission
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    handleLogin(username, password);
  });
}

function handleLogin(username, password) {
  const user = userData.users.find(u => u.username === username && u.password === password);
  
  if (user) {
    currentUser = user;
    showApp();
  } else {
    alert('Invalid credentials. Please try again.');
  }
}

function showApp() {
  document.getElementById('loginContainer').classList.add('hidden');
  document.getElementById('appContainer').classList.remove('hidden');
  
  // Initialize app for current user
  initNavigation();
  updateUserInfo();
  loadDashboard();
  showPage('dashboard');
}

function logout() {
  if (confirm('Are you sure you want to logout?')) {
    currentUser = null;
    document.getElementById('loginContainer').classList.remove('hidden');
    document.getElementById('appContainer').classList.add('hidden');
    
    // Reset form
    document.getElementById('loginForm').reset();
    
    // Clear any stored data
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
  }
}

// Navigation
function initNavigation() {
  const config = navigationConfig[currentUser.role];
  const sidebarNav = document.getElementById('sidebarNav');
  const sidebarNavMobile = document.getElementById('sidebarNavMobile');
  const bottomNav = document.getElementById('bottomNav');
  
  // Clear existing navigation
  sidebarNav.innerHTML = '';
  sidebarNavMobile.innerHTML = '';
  bottomNav.innerHTML = '';
  
  // Desktop sidebar
  config.forEach(item => {
    const navItem = document.createElement('button');
    navItem.className = 'nav-item';
    navItem.dataset.page = item.id;
    navItem.title = item.title;
    navItem.innerHTML = `<i class="${item.icon}"></i>`;
    navItem.addEventListener('click', () => {
      showPage(item.id);
      setActiveNav(item.id);
    });
    sidebarNav.appendChild(navItem);
  });
  
  // Mobile sidebar
  config.forEach(item => {
    const navItem = document.createElement('button');
    navItem.className = 'nav-item-mobile';
    navItem.dataset.page = item.id;
    navItem.innerHTML = `<i class="${item.icon}"></i><span>${item.title}</span>`;
    navItem.addEventListener('click', () => {
      showPage(item.id);
      closeMobileSidebar();
    });
    sidebarNavMobile.appendChild(navItem);
  });
  
  // Add logout to mobile sidebar
  const logoutItemMobile = document.createElement('button');
  logoutItemMobile.className = 'nav-item-mobile';
  logoutItemMobile.innerHTML = `<i class="bi-box-arrow-right"></i><span>Logout</span>`;
  logoutItemMobile.addEventListener('click', () => {
    closeMobileSidebar();
    logout();
  });
  sidebarNavMobile.appendChild(logoutItemMobile);
  
  // Bottom navigation (mobile) - show first 4 items + more
  const mobileItems = config.slice(0, 4);
  mobileItems.forEach((item, index) => {
    const navItem = document.createElement('button');
    navItem.className = 'bottom-nav-item';
    navItem.dataset.page = item.id;
    if (index === 0) navItem.classList.add('active');
    navItem.innerHTML = `<i class="${item.icon}"></i><span>${item.title}</span>`;
    navItem.addEventListener('click', () => {
      showPage(item.id);
      setActiveBottomNav(navItem);
    });
    bottomNav.appendChild(navItem);
  });
  
  // More button for mobile
  if (config.length > 4) {
    const moreBtn = document.createElement('button');
    moreBtn.className = 'bottom-nav-item';
    moreBtn.innerHTML = `<i class="bi-three-dots"></i><span>More</span>`;
    moreBtn.addEventListener('click', () => {
      document.getElementById('sidebarMobile').classList.add('open');
      document.getElementById('sidebarOverlay').classList.add('show');
    });
    bottomNav.appendChild(moreBtn);
  }
  
  // Set first item as active
  setActiveNav(config[0].id);
  
  // Logout button - Make sure it's visible and functional
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
    logoutBtn.style.display = 'flex'; // Ensure it's visible
  }
}

function showPage(pageId) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(page => {
    page.classList.remove('active');
  });
  
  // Show target page
  const targetPage = document.getElementById(pageId);
  if (targetPage) {
    targetPage.classList.add('active');
    loadPageContent(pageId);
  }
  
  // Update page title
  const config = navigationConfig[currentUser.role];
  const pageConfig = config.find(item => item.id === pageId);
  if (pageConfig) {
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle) {
      pageTitle.textContent = pageConfig.title;
    }
  }
}

function setActiveNav(pageId) {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
    if (item.dataset.page === pageId) {
      item.classList.add('active');
    }
  });
}

function setActiveBottomNav(activeItem) {
  document.querySelectorAll('.bottom-nav-item').forEach(item => {
    item.classList.remove('active');
  });
  activeItem.classList.add('active');
}

// Mobile sidebar functionality
function initMobileSidebar() {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const closeMobileSidebarBtn = document.getElementById('closeMobileSidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
      document.getElementById('sidebarMobile').classList.add('open');
      sidebarOverlay.classList.add('show');
    });
  }
  
  if (closeMobileSidebarBtn) {
    closeMobileSidebarBtn.addEventListener('click', () => {
      closeMobileSidebarHandler();
    });
  }
  
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
      closeMobileSidebarHandler();
    });
  }
}

function closeMobileSidebar() {
  closeMobileSidebarHandler();
}

function closeMobileSidebarHandler() {
  const sidebarMobile = document.getElementById('sidebarMobile');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  
  if (sidebarMobile) sidebarMobile.classList.remove('open');
  if (sidebarOverlay) sidebarOverlay.classList.remove('show');
}

// Update user info in header
function updateUserInfo() {
  const userName = document.getElementById('userName');
  const userRole = document.getElementById('userRole');
  const welcomeUser = document.getElementById('welcomeUser');
  
  if (userName) userName.textContent = currentUser.name;
  if (userRole) userRole.textContent = currentUser.role.toUpperCase();
  if (welcomeUser) welcomeUser.textContent = currentUser.name.split(' ')[0];
}

// Load page content based on current user role
function loadPageContent(pageId) {
  switch (pageId) {
    case 'dashboard':
      loadDashboard();
      break;
    case 'employees':
      loadEmployees();
      break;
    case 'attendance':
      loadAttendance();
      break;
    case 'leaves':
      loadLeaves();
      break;
    case 'payroll':
      loadPayroll();
      break;
    case 'profile':
      loadProfile();
      break;
  }
}

// Dashboard
function loadDashboard() {
  const metricsGrid = document.getElementById('metricsGrid');
  const dashboardCards = document.getElementById('dashboardCards');
  const dashboardTitle = document.getElementById('dashboardTitle');
  
  // Set title based on role
  if (currentUser.role === 'admin') {
    dashboardTitle.textContent = 'Admin Dashboard';
  } else if (currentUser.role === 'hr') {
    dashboardTitle.textContent = 'HR Dashboard';
  } else {
    dashboardTitle.textContent = 'My Dashboard';
  }
  
  // Load metrics based on role
  if (currentUser.role === 'admin') {
    loadAdminMetrics(metricsGrid);
  } else if (currentUser.role === 'hr') {
    loadHRMetrics(metricsGrid);
  } else {
    loadEmployeeMetrics(metricsGrid);
  }
  
  // Load dashboard cards
  loadDashboardCards(dashboardCards);
}

function loadAdminMetrics(container) {
  const totalEmployees = userData.users.length;
  const presentToday = userData.attendance_records.filter(r => r.status === 'Present' || r.status === 'Late').length;
  const pendingLeaves = userData.leave_requests.filter(r => r.status === 'Pending').length;
  const processingPayroll = userData.payroll_records.filter(r => r.status === 'Processing').length;
  
  container.innerHTML = `
    <div class="metric-card">
      <div class="metric-value">${totalEmployees}</div>
      <div class="metric-label">Total Employees</div>
      <div class="metric-icon"><i class="bi bi-people"></i></div>
    </div>
    <div class="metric-card success">
      <div class="metric-value">${presentToday}</div>
      <div class="metric-label">Present Today</div>
      <div class="metric-icon"><i class="bi bi-check-circle"></i></div>
    </div>
    <div class="metric-card warning">
      <div class="metric-value">${pendingLeaves}</div>
      <div class="metric-label">Pending Leaves</div>
      <div class="metric-icon"><i class="bi bi-calendar-x"></i></div>
    </div>
    <div class="metric-card info">
      <div class="metric-value">${processingPayroll}</div>
      <div class="metric-label">Processing Payroll</div>
      <div class="metric-icon"><i class="bi bi-currency-dollar"></i></div>
    </div>
  `;
}

function loadHRMetrics(container) {
  // HR sees employees excluding admin
  const hrVisibleEmployees = userData.users.filter(u => u.role !== 'admin');
  const presentToday = userData.attendance_records.filter(r => r.status === 'Present' || r.status === 'Late').filter(r => {
    const user = userData.users.find(u => u.name === r.employee_name);
    return user && user.role !== 'admin';
  }).length;
  const pendingLeaves = userData.leave_requests.filter(r => r.status === 'Pending').length;
  
  container.innerHTML = `
    <div class="metric-card">
      <div class="metric-value">${hrVisibleEmployees.length}</div>
      <div class="metric-label">Employees</div>
      <div class="metric-icon"><i class="bi bi-people"></i></div>
    </div>
    <div class="metric-card success">
      <div class="metric-value">${presentToday}</div>
      <div class="metric-label">Present Today</div>
      <div class="metric-icon"><i class="bi bi-check-circle"></i></div>
    </div>
    <div class="metric-card warning">
      <div class="metric-value">${pendingLeaves}</div>
      <div class="metric-label">Pending Leaves</div>
      <div class="metric-icon"><i class="bi bi-calendar-x"></i></div>
    </div>
  `;
}

function loadEmployeeMetrics(container) {
  // Employee sees only their own data
  const myAttendance = userData.attendance_records.find(r => r.employee_name === currentUser.name);
  const myLeaves = userData.leave_requests.filter(r => r.employee_name === currentUser.name);
  const pendingLeaves = myLeaves.filter(r => r.status === 'Pending').length;
  const myPayroll = userData.payroll_records.find(r => r.employee_name === currentUser.name);
  
  container.innerHTML = `
    <div class="metric-card ${myAttendance ? getStatusClass(myAttendance.status).replace('error', 'danger') : 'danger'}">
      <div class="metric-value">${myAttendance ? myAttendance.status : 'No Record'}</div>
      <div class="metric-label">Today's Status</div>
      <div class="metric-icon"><i class="bi bi-clock"></i></div>
    </div>
    <div class="metric-card warning">
      <div class="metric-value">${pendingLeaves}</div>
      <div class="metric-label">Pending Leaves</div>
      <div class="metric-icon"><i class="bi bi-calendar-x"></i></div>
    </div>
    <div class="metric-card info">
      <div class="metric-value">${myLeaves.length}</div>
      <div class="metric-label">Total Leave Requests</div>
      <div class="metric-icon"><i class="bi bi-calendar-check"></i></div>
    </div>
    <div class="metric-card ${myPayroll ? getStatusClass(myPayroll.status).replace('error', 'danger') : 'info'}">
      <div class="metric-value">${myPayroll ? myPayroll.status : 'N/A'}</div>
      <div class="metric-label">Payroll Status</div>
      <div class="metric-icon"><i class="bi bi-currency-dollar"></i></div>
    </div>
  `;
}

function loadDashboardCards(container) {
  if (currentUser.role === 'employee') {
    // Employee sees recent activity
    const myLeaves = userData.leave_requests.filter(r => r.employee_name === currentUser.name);
    const myAttendance = userData.attendance_records.find(r => r.employee_name === currentUser.name);
    
    container.innerHTML = `
      <div class="card">
        <div class="card__body">
          <h3 class="card-title">Recent Leave Requests</h3>
          ${myLeaves.length > 0 ? myLeaves.map(leave => `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-light);">
              <div>
                <div style="font-weight: 600; color: var(--text-primary);">${leave.leave_type}</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">${leave.start_date} to ${leave.end_date}</div>
              </div>
              <span class="status status--${getStatusClass(leave.status)}">${leave.status}</span>
            </div>
          `).join('') : '<p style="color: var(--text-secondary);">No leave requests found.</p>'}
        </div>
      </div>
      <div class="card">
        <div class="card__body">
          <h3 class="card-title">Today's Attendance</h3>
          ${myAttendance ? `
            <div style="padding: 1rem 0;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Status:</span>
                <span class="status status--${getStatusClass(myAttendance.status)}">${myAttendance.status}</span>
              </div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Clock In:</span>
                <span>${myAttendance.clock_in || 'Not clocked in'}</span>
              </div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Clock Out:</span>
                <span>${myAttendance.clock_out || 'Not clocked out'}</span>
              </div>
              <div style="display: flex; justify-content: space-between;">
                <span>Total Hours:</span>
                <span>${myAttendance.hours}</span>
              </div>
            </div>
          ` : '<p style="color: var(--text-secondary);">No attendance record found for today.</p>'}
        </div>
      </div>
    `;
  } else {
    // Admin/HR sees recent activities
    container.innerHTML = `
      <div class="card">
        <div class="card__body">
          <h3 class="card-title">Recent Activities</h3>
          <div style="color: var(--text-secondary);">Recent system activities and notifications will appear here.</div>
        </div>
      </div>
      <div class="card">
        <div class="card__body">
          <h3 class="card-title">Quick Actions</h3>
          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <button class="btn btn--primary btn--sm">Add Employee</button>
            <button class="btn btn--secondary btn--sm">Generate Report</button>
            <button class="btn btn--secondary btn--sm">Process Payroll</button>
          </div>
        </div>
      </div>
    `;
  }
}

// Employees page
function loadEmployees() {
  if (currentUser.role === 'employee') {
    // Employees can't access this page
    showPage('dashboard');
    return;
  }
  
  const employeesGrid = document.getElementById('employeesGrid');
  const addEmployeeBtn = document.getElementById('addEmployeeBtn');
  
  // Show/hide add button based on role
  if (currentUser.role === 'hr' || currentUser.role === 'admin') {
    if (addEmployeeBtn) addEmployeeBtn.style.display = 'flex';
  } else {
    if (addEmployeeBtn) addEmployeeBtn.style.display = 'none';
  }
  
  // Filter employees based on role
  let employees = userData.users;
  if (currentUser.role === 'hr') {
    // HR can't see admin
    employees = employees.filter(u => u.role !== 'admin');
  }
  
  if (employeesGrid) {
    employeesGrid.innerHTML = employees.map(employee => `
      <div class="employee-card">
        <div class="employee-header">
          <div class="employee-avatar">${getInitials(employee.name)}</div>
          <div>
            <div class="employee-name">${employee.name}</div>
            <div class="employee-position">${employee.position}</div>
          </div>
        </div>
        <div class="employee-details">
          <div><strong>Department:</strong> ${employee.department}</div>
          <div><strong>Email:</strong> ${employee.email}</div>
          <div><strong>Role:</strong> ${employee.role.charAt(0).toUpperCase() + employee.role.slice(1)}</div>
        </div>
        <div class="employee-actions">
          <button class="btn btn--secondary btn--sm">View</button>
          <button class="btn btn--secondary btn--sm">Edit</button>
        </div>
      </div>
    `).join('');
  }
}

// Attendance page
function loadAttendance() {
  const tableHeader = document.getElementById('attendanceTableHeader');
  const tableBody = document.getElementById('attendanceTableBody');
  const clockInOutBtn = document.getElementById('clockInOutBtn');
  
  if (!tableHeader || !tableBody) return;
  
  // Show/hide clock button for employees only
  if (currentUser.role === 'employee') {
    if (clockInOutBtn) clockInOutBtn.style.display = 'flex';
    tableHeader.innerHTML = `
      <th>Date</th>
      <th>Clock In</th>
      <th>Clock Out</th>
      <th>Hours</th>
      <th>Status</th>
    `;
    
    // Employee sees only their own attendance
    const myAttendance = userData.attendance_records.filter(r => r.employee_name === currentUser.name);
    tableBody.innerHTML = myAttendance.map(record => `
      <tr>
        <td>${record.date}</td>
        <td>${record.clock_in || '-'}</td>
        <td>${record.clock_out || '-'}</td>
        <td>${record.hours}</td>
        <td><span class="status status--${getStatusClass(record.status)}">${record.status}</span></td>
      </tr>
    `).join('');
    
  } else {
    if (clockInOutBtn) clockInOutBtn.style.display = 'none';
    tableHeader.innerHTML = `
      <th>Employee</th>
      <th>Department</th>
      <th>Clock In</th>
      <th>Clock Out</th>
      <th>Hours</th>
      <th>Status</th>
      <th>Actions</th>
    `;
    
    // Filter records based on role
    let records = userData.attendance_records;
    if (currentUser.role === 'hr') {
      records = records.filter(r => {
        const user = userData.users.find(u => u.name === r.employee_name);
        return user && user.role !== 'admin';
      });
    }
    
    tableBody.innerHTML = records.map(record => {
      const employee = userData.users.find(u => u.name === record.employee_name);
      return `
        <tr>
          <td>
            <div class="table-employee">
              <div class="employee-avatar">${getInitials(record.employee_name)}</div>
              <div class="employee-info">
                <h4>${record.employee_name}</h4>
                <p>ID: ${employee ? employee.id : 'N/A'}</p>
              </div>
            </div>
          </td>
          <td>${employee ? employee.department : 'N/A'}</td>
          <td>${record.clock_in || '-'}</td>
          <td>${record.clock_out || '-'}</td>
          <td>${record.hours}</td>
          <td><span class="status status--${getStatusClass(record.status)}">${record.status}</span></td>
          <td>
            <button class="btn btn--secondary btn--sm">View</button>
            <button class="btn btn--secondary btn--sm">Edit</button>
          </td>
        </tr>
      `;
    }).join('');
  }
}

// Leaves page
function loadLeaves() {
  const tableHeader = document.getElementById('leavesTableHeader');
  const tableBody = document.getElementById('leavesTableBody');
  const requestLeaveBtn = document.getElementById('requestLeaveBtn');
  
  if (!tableHeader || !tableBody) return;
  
  if (currentUser.role === 'employee') {
    if (requestLeaveBtn) requestLeaveBtn.style.display = 'flex';
    tableHeader.innerHTML = `
      <th>Leave Type</th>
      <th>Start Date</th>
      <th>End Date</th>
      <th>Days</th>
      <th>Status</th>
      <th>Applied Date</th>
    `;
    
    // Employee sees only their own leaves
    const myLeaves = userData.leave_requests.filter(r => r.employee_name === currentUser.name);
    tableBody.innerHTML = myLeaves.map(request => `
      <tr>
        <td>${request.leave_type}</td>
        <td>${request.start_date}</td>
        <td>${request.end_date}</td>
        <td>${request.days} day${request.days > 1 ? 's' : ''}</td>
        <td><span class="status status--${getStatusClass(request.status)}">${request.status}</span></td>
        <td>${request.applied_date}</td>
      </tr>
    `).join('');
    
  } else {
    if (requestLeaveBtn) requestLeaveBtn.style.display = 'none';
    tableHeader.innerHTML = `
      <th>Employee</th>
      <th>Leave Type</th>
      <th>Start Date</th>
      <th>End Date</th>
      <th>Days</th>
      <th>Status</th>
      <th>Applied Date</th>
      <th>Actions</th>
    `;
    
    tableBody.innerHTML = userData.leave_requests.map(request => `
      <tr>
        <td>
          <div class="table-employee">
            <div class="employee-avatar">${getInitials(request.employee_name)}</div>
            <div class="employee-info">
              <h4>${request.employee_name}</h4>
            </div>
          </div>
        </td>
        <td>${request.leave_type}</td>
        <td>${request.start_date}</td>
        <td>${request.end_date}</td>
        <td>${request.days} day${request.days > 1 ? 's' : ''}</td>
        <td><span class="status status--${getStatusClass(request.status)}">${request.status}</span></td>
        <td>${request.applied_date}</td>
        <td>
          ${request.status === 'Pending' ? `
            <button class="btn btn--primary btn--sm">Approve</button>
            <button class="btn btn--secondary btn--sm">Reject</button>
          ` : `
            <button class="btn btn--secondary btn--sm">View</button>
          `}
        </td>
      </tr>
    `).join('');
  }
}

// Payroll page
function loadPayroll() {
  const tableHeader = document.getElementById('payrollTableHeader');
  const tableBody = document.getElementById('payrollTableBody');
  
  if (!tableHeader || !tableBody) return;
  
  if (currentUser.role === 'employee') {
    tableHeader.innerHTML = `
      <th>Month</th>
      <th>Basic Salary</th>
      <th>Allowances</th>
      <th>Deductions</th>
      <th>Net Salary</th>
      <th>Status</th>
    `;
    
    // Employee sees only their own payroll
    const myPayroll = userData.payroll_records.filter(r => r.employee_name === currentUser.name);
    tableBody.innerHTML = myPayroll.map(record => `
      <tr>
        <td>${record.month}</td>
        <td>${formatCurrency(record.basic_salary)}</td>
        <td>${formatCurrency(record.allowances)}</td>
        <td>${formatCurrency(record.deductions)}</td>
        <td><strong>${formatCurrency(record.net_salary)}</strong></td>
        <td><span class="status status--${getStatusClass(record.status)}">${record.status}</span></td>
      </tr>
    `).join('');
    
  } else {
    tableHeader.innerHTML = `
      <th>Employee</th>
      <th>Department</th>
      <th>Basic Salary</th>
      <th>Allowances</th>
      <th>Deductions</th>
      <th>Net Salary</th>
      <th>Status</th>
      <th>Actions</th>
    `;
    
    // Filter records based on role
    let records = userData.payroll_records;
    if (currentUser.role === 'hr') {
      records = records.filter(r => {
        const user = userData.users.find(u => u.name === r.employee_name);
        return user && user.role !== 'admin';
      });
    }
    
    tableBody.innerHTML = records.map(record => {
      const employee = userData.users.find(u => u.name === record.employee_name);
      return `
        <tr>
          <td>
            <div class="table-employee">
              <div class="employee-avatar">${getInitials(record.employee_name)}</div>
              <div class="employee-info">
                <h4>${record.employee_name}</h4>
              </div>
            </div>
          </td>
          <td>${employee ? employee.department : 'N/A'}</td>
          <td>${formatCurrency(record.basic_salary)}</td>
          <td>${formatCurrency(record.allowances)}</td>
          <td>${formatCurrency(record.deductions)}</td>
          <td><strong>${formatCurrency(record.net_salary)}</strong></td>
          <td><span class="status status--${getStatusClass(record.status)}">${record.status}</span></td>
          <td>
            <button class="btn btn--secondary btn--sm">View</button>
            ${record.status === 'Processing' ? '<button class="btn btn--primary btn--sm">Process</button>' : ''}
          </td>
        </tr>
      `;
    }).join('');
  }
}

// Profile page (employee only)
function loadProfile() {
  const profileAvatar = document.getElementById('profileAvatar');
  const profileName = document.getElementById('profileName');
  const profilePosition = document.getElementById('profilePosition');
  const profileDepartment = document.getElementById('profileDepartment');
  const profileEmail = document.getElementById('profileEmail');
  const profileId = document.getElementById('profileId');
  
  if (profileAvatar) profileAvatar.textContent = getInitials(currentUser.name);
  if (profileName) profileName.textContent = currentUser.name;
  if (profilePosition) profilePosition.textContent = currentUser.position;
  if (profileDepartment) profileDepartment.textContent = currentUser.department;
  if (profileEmail) profileEmail.textContent = currentUser.email;
  if (profileId) profileId.textContent = currentUser.id;
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
  initAuth();
  initMobileSidebar();
  
  // Set today's date
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('attendanceDate');
  if (dateInput) {
    dateInput.value = today;
  }
});