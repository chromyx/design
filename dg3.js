// Attendix Professional HR Management System - Complete AJAX Implementation
class AttendixApp {
    constructor() {
        this.currentUser = null;
        this.currentPage = 'dashboard';
        this.charts = {};
        
        // Initialize application data from provided JSON
        this.initializeData();
        
        // Bind event listeners
        this.bindEvents();
        
        // Show loading screen initially
        this.showLoading();
        
        // Check for existing session
        setTimeout(() => {
            this.checkExistingSession();
        }, 1500);
    }

    initializeData() {
        // Initialize with provided data structure
        this.users = [
            {
                id: 1,
                username: "admin", 
                password: "admin123",
                role: "admin",
                email: "admin@attendix.com",
                phone_number: "+1-555-0001",
                first_name: "System",
                last_name: "Administrator",
                is_active: true
            },
            {
                id: 2,
                username: "hr_manager",
                password: "hr123", 
                role: "hr",
                email: "sarah@attendix.com", 
                phone_number: "+1-555-0002",
                first_name: "Sarah",
                last_name: "Johnson",
                is_active: true
            },
            {
                id: 3,
                username: "john_doe",
                password: "emp123",
                role: "employee", 
                email: "john@attendix.com",
                phone_number: "+1-555-0003", 
                first_name: "John",
                last_name: "Doe",
                is_active: true
            },
            {
                id: 4,
                username: "alice_smith",
                password: "emp123",
                role: "employee",
                email: "alice@attendix.com", 
                phone_number: "+1-555-0004",
                first_name: "Alice",
                last_name: "Smith",
                is_active: true
            }
        ];

        this.departments = [
            {
                id: 1,
                name: "Human Resources",
                description: "Employee management and organizational development",
                manager: 2,
                budget: 150000,
                is_active: true,
                employee_count: 5
            },
            {
                id: 2,
                name: "Engineering", 
                description: "Software development and technical operations",
                manager: 3,
                budget: 500000,
                is_active: true,
                employee_count: 25
            }
        ];

        this.job_positions = [
            {
                id: 1,
                title: "System Administrator",
                department: 1,
                description: "Manage IT infrastructure and systems",
                requirements: "5+ years experience in system administration",
                min_salary: 70000,
                max_salary: 90000,
                is_active: true
            },
            {
                id: 2,
                title: "HR Manager",
                department: 1, 
                description: "Oversee human resources operations",
                requirements: "3+ years HR experience, SHRM certification preferred",
                min_salary: 60000,
                max_salary: 80000,
                is_active: true
            },
            {
                id: 3,
                title: "Senior Developer",
                department: 2,
                description: "Lead development projects and mentor junior developers", 
                requirements: "5+ years software development experience",
                min_salary: 80000,
                max_salary: 120000,
                is_active: true
            }
        ];

        this.employees = [
            {
                id: 1,
                user_id: 1,
                employee_id: "EMP001", 
                department: 1,
                position: 1,
                status: "active",
                hire_date: "2020-01-15",
                base_salary: 75000
            },
            {
                id: 2,
                user_id: 2,
                employee_id: "EMP002",
                department: 1,
                position: 2,
                status: "active",
                hire_date: "2020-03-20",
                base_salary: 65000
            },
            {
                id: 3,
                user_id: 3,
                employee_id: "EMP003",
                department: 2,
                position: 3,
                status: "active",
                hire_date: "2021-06-15",
                base_salary: 85000
            }
        ];

        // Sample attendance records
        this.attendance_records = [
            {
                id: 1,
                employee_id: 1,
                date: "2024-03-15",
                check_in_time: "2024-03-15T08:00:00",
                check_out_time: "2024-03-15T17:00:00",
                work_hours: 8.0,
                overtime_hours: 0,
                is_late: false,
                is_absent: false,
                notes: "Regular work day"
            },
            {
                id: 2,
                employee_id: 2,
                date: "2024-03-15",
                check_in_time: "2024-03-15T08:30:00",
                check_out_time: "2024-03-15T17:30:00",
                work_hours: 8.0,
                overtime_hours: 1.0,
                is_late: true,
                is_absent: false,
                notes: "Traffic delay"
            }
        ];

        // Sample leave requests
        this.leave_requests = [
            {
                id: 1,
                employee_id: 3,
                leave_type: "sick",
                start_date: "2024-03-15",
                end_date: "2024-03-15", 
                days_requested: 1,
                reason: "Flu symptoms",
                status: "approved",
                approved_by: 2,
                approved_at: "2024-03-14T10:00:00",
                rejection_reason: ""
            }
        ];

        // Sample payroll records
        this.payroll_records = [
            {
                id: 1,
                employee_id: 1,
                pay_period_start: "2024-03-01",
                pay_period_end: "2024-03-31",
                base_salary: 75000,
                hours_worked: 160,
                overtime_hours: 10,
                overtime_pay: 500,
                deductions: 8000,
                bonuses: 2000,
                net_salary: 69500,
                status: "paid",
                created_by: 2,
                approved_by: 1,
                approved_at: "2024-03-30T14:00:00"
            }
        ];
    }

    bindEvents() {
        // Login form
        document.getElementById('loginForm')?.addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('passwordToggle')?.addEventListener('click', () => this.togglePassword());

        // Mobile navigation
        document.getElementById('mobileMenuBtn')?.addEventListener('click', () => this.toggleMobileSidebar());
        document.getElementById('closeMobileSidebar')?.addEventListener('click', () => this.closeMobileSidebar());
        document.getElementById('sidebarOverlay')?.addEventListener('click', () => this.closeMobileSidebar());

        // Logout
        document.addEventListener('click', (e) => {
            if (e.target.closest('#logoutBtn')) {
                e.preventDefault();
                this.logout();
            }
        });

        // Notifications
        document.getElementById('notificationBell')?.addEventListener('click', () => this.toggleNotifications());
        document.getElementById('closeNotifications')?.addEventListener('click', () => this.closeNotifications());

        // Modal events - ALL SIX MODALS
        this.bindModalEvents();

        // Filter events
        this.bindFilterEvents();

        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeAllModals();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
                this.closeNotifications();
            }
        });
    }

    bindModalEvents() {
        // MODAL 1: Add User Modal
        document.getElementById('addUserBtn')?.addEventListener('click', () => this.openAddUserModal());
        document.getElementById('closeUserModal')?.addEventListener('click', () => this.closeModal('addUserModal'));
        document.getElementById('cancelUserModal')?.addEventListener('click', () => this.closeModal('addUserModal'));
        document.getElementById('addUserForm')?.addEventListener('submit', (e) => this.handleAddUser(e));

        // MODAL 2: Add Payroll Modal
        document.getElementById('addPayrollBtn')?.addEventListener('click', () => this.openAddPayrollModal());
        document.getElementById('closePayrollModal')?.addEventListener('click', () => this.closeModal('addPayrollModal'));
        document.getElementById('cancelPayrollModal')?.addEventListener('click', () => this.closeModal('addPayrollModal'));
        document.getElementById('addPayrollForm')?.addEventListener('submit', (e) => this.handleAddPayroll(e));

        // MODAL 3: Add Attendance Modal
        document.getElementById('addAttendanceBtn')?.addEventListener('click', () => this.openAddAttendanceModal());
        document.getElementById('closeAttendanceModal')?.addEventListener('click', () => this.closeModal('addAttendanceModal'));
        document.getElementById('cancelAttendanceModal')?.addEventListener('click', () => this.closeModal('addAttendanceModal'));
        document.getElementById('addAttendanceForm')?.addEventListener('submit', (e) => this.handleAddAttendance(e));

        // MODAL 4: Add Department Modal
        document.getElementById('addDepartmentBtn')?.addEventListener('click', () => this.openAddDepartmentModal());
        document.getElementById('closeDepartmentModal')?.addEventListener('click', () => this.closeModal('addDepartmentModal'));
        document.getElementById('cancelDepartmentModal')?.addEventListener('click', () => this.closeModal('addDepartmentModal'));
        document.getElementById('addDepartmentForm')?.addEventListener('submit', (e) => this.handleAddDepartment(e));

        // MODAL 5: Add Leave Request Modal
        document.getElementById('addLeaveRequestBtn')?.addEventListener('click', () => this.openAddLeaveRequestModal());
        document.getElementById('closeLeaveRequestModal')?.addEventListener('click', () => this.closeModal('addLeaveRequestModal'));
        document.getElementById('cancelLeaveRequestModal')?.addEventListener('click', () => this.closeModal('addLeaveRequestModal'));
        document.getElementById('addLeaveRequestForm')?.addEventListener('submit', (e) => this.handleAddLeaveRequest(e));

        // MODAL 6: Add Job Position Modal
        document.getElementById('addJobPositionBtn')?.addEventListener('click', () => this.openAddJobPositionModal());
        document.getElementById('closeJobPositionModal')?.addEventListener('click', () => this.closeModal('addJobPositionModal'));
        document.getElementById('cancelJobPositionModal')?.addEventListener('click', () => this.closeModal('addJobPositionModal'));
        document.getElementById('addJobPositionForm')?.addEventListener('submit', (e) => this.handleAddJobPosition(e));

        // Auto-calculations
        this.bindAutoCalculations();
    }

    bindAutoCalculations() {
        // Payroll auto-calculations
        ['payrollBaseSalary', 'payrollOvertimePay', 'payrollDeductions', 'payrollBonuses'].forEach(id => {
            document.getElementById(id)?.addEventListener('input', () => this.calculateNetSalary());
        });

        // Attendance auto-calculations
        ['attendanceCheckIn', 'attendanceCheckOut'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', () => this.calculateWorkHours());
        });

        // Leave request auto-calculations
        ['leaveStartDate', 'leaveEndDate'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', () => this.calculateLeaveDays());
        });

        // Role-based field visibility
        document.getElementById('leaveStatus')?.addEventListener('change', (e) => {
            const approvalSection = document.getElementById('leaveApprovalSection');
            if (e.target.value === 'approved' || e.target.value === 'rejected') {
                approvalSection?.classList.remove('hidden');
            } else {
                approvalSection?.classList.add('hidden');
            }
        });

        // Salary validation
        ['positionMinSalary', 'positionMaxSalary'].forEach(id => {
            document.getElementById(id)?.addEventListener('input', () => this.validateSalaryRange());
        });
    }

    bindFilterEvents() {
        // Employee filters
        document.getElementById('employeeSearch')?.addEventListener('input', () => this.filterEmployees());
        document.getElementById('departmentFilter')?.addEventListener('change', () => this.filterEmployees());
        document.getElementById('roleFilter')?.addEventListener('change', () => this.filterEmployees());

        // Leave filters
        document.getElementById('leaveStatusFilter')?.addEventListener('change', () => this.filterLeaves());

        // Payroll filters
        document.getElementById('payrollMonthFilter')?.addEventListener('change', () => this.filterPayroll());
    }

    // Loading and Authentication
    showLoading() {
        document.getElementById('loadingScreen').style.display = 'flex';
    }

    hideLoading() {
        const loadingScreen = document.getElementById('loadingScreen');
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 300);
    }

    checkExistingSession() {
        // Check for saved session (in production, would validate with backend)
        const savedUser = sessionStorage.getItem('attendix_user');
        if (savedUser) {
            try {
                this.currentUser = JSON.parse(savedUser);
                this.showApp();
            } catch (e) {
                this.showLogin();
            }
        } else {
            this.showLogin();
        }
        this.hideLoading();
    }

    showLogin() {
        document.getElementById('loginPage').style.display = 'flex';
        document.getElementById('appContainer').classList.add('hidden');
    }

    showApp() {
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('appContainer').classList.remove('hidden');
        this.initializeApp();
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<i class="bi bi-arrow-clockwise spinner"></i> Signing in...';
        submitBtn.disabled = true;

        // Simulate AJAX call
        await this.simulateAjaxDelay();

        try {
            const user = this.authenticateUser(username, password);
            if (user) {
                this.currentUser = user;
                
                if (rememberMe) {
                    sessionStorage.setItem('attendix_user', JSON.stringify(user));
                }
                
                this.showSuccess('Login successful! Welcome to Attendix.');
                setTimeout(() => {
                    this.showApp();
                }, 1000);
            } else {
                this.showError('Invalid credentials. Please check your username and password.');
            }
        } catch (error) {
            this.showError('Login failed. Please try again.');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    authenticateUser(username, password) {
        return this.users.find(user => 
            (user.username === username || user.email === username) && 
            user.password === password && 
            user.is_active
        );
    }

    togglePassword() {
        const passwordInput = document.getElementById('loginPassword');
        const passwordToggle = document.getElementById('passwordToggle');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            passwordToggle.innerHTML = '<i class="bi bi-eye-slash"></i>';
        } else {
            passwordInput.type = 'password';
            passwordToggle.innerHTML = '<i class="bi bi-eye"></i>';
        }
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            sessionStorage.removeItem('attendix_user');
            this.currentUser = null;
            this.closeAllModals();
            this.closeNotifications();
            
            // Reset app state
            this.currentPage = 'dashboard';
            if (this.charts.attendance) this.charts.attendance.destroy();
            if (this.charts.department) this.charts.department.destroy();
            this.charts = {};
            
            this.showLogin();
            this.showInfo('You have been logged out successfully.');
        }
    }

    // App Initialization
    initializeApp() {
        this.setupNavigation();
        this.updateUserInfo();
        this.loadDashboard();
        this.updateNotifications();
        this.populateDropdowns();
    }

    setupNavigation() {
        const roleNavigation = {
            admin: [
                { id: 'dashboard', title: 'Dashboard', icon: 'bi-speedometer2' },
                { id: 'employees', title: 'Employees', icon: 'bi-people' },
                { id: 'attendance', title: 'Attendance', icon: 'bi-clock-history' },
                { id: 'leaves', title: 'Leave Management', icon: 'bi-calendar-x' },
                { id: 'departments', title: 'Departments', icon: 'bi-diagram-3' },
                { id: 'positions', title: 'Job Positions', icon: 'bi-briefcase' },
                { id: 'payroll', title: 'Payroll', icon: 'bi-currency-dollar' }
            ],
            hr: [
                { id: 'dashboard', title: 'Dashboard', icon: 'bi-speedometer2' },
                { id: 'employees', title: 'Employees', icon: 'bi-people' },
                { id: 'attendance', title: 'Attendance', icon: 'bi-clock-history' },
                { id: 'leaves', title: 'Leave Management', icon: 'bi-calendar-x' },
                { id: 'departments', title: 'Departments', icon: 'bi-diagram-3' },
                { id: 'positions', title: 'Job Positions', icon: 'bi-briefcase' },
                { id: 'payroll', title: 'Payroll', icon: 'bi-currency-dollar' }
            ],
            employee: [
                { id: 'dashboard', title: 'My Dashboard', icon: 'bi-speedometer2' },
                { id: 'attendance', title: 'My Attendance', icon: 'bi-clock-history' },
                { id: 'leaves', title: 'My Leaves', icon: 'bi-calendar-x' },
                { id: 'payroll', title: 'My Payroll', icon: 'bi-currency-dollar' }
            ]
        };

        const navItems = roleNavigation[this.currentUser.role] || roleNavigation.employee;
        this.renderNavigation(navItems);
        this.bindNavigationEvents(navItems);
    }

    renderNavigation(navItems) {
        // Desktop sidebar navigation
        const sidebarNav = document.getElementById('sidebarNav');
        if (sidebarNav) {
            sidebarNav.innerHTML = navItems.map(item => `
                <button class="nav-item ${item.id === 'dashboard' ? 'active' : ''}" 
                        data-page="${item.id}" title="${item.title}">
                    <i class="${item.icon}"></i>
                </button>
            `).join('');
        }

        // Mobile sidebar navigation
        const mobileSidebarNav = document.getElementById('mobileSidebarNav');
        if (mobileSidebarNav) {
            mobileSidebarNav.innerHTML = navItems.map(item => `
                <button class="nav-item-mobile ${item.id === 'dashboard' ? 'active' : ''}" 
                        data-page="${item.id}">
                    <i class="${item.icon}"></i>
                    <span>${item.title}</span>
                </button>
            `).join('');
        }

        // Mobile bottom navigation
        const bottomNav = document.getElementById('bottomNav');
        if (bottomNav) {
            const bottomNavItems = navItems.slice(0, 4);
            bottomNav.innerHTML = bottomNavItems.map(item => `
                <button class="bottom-nav-item ${item.id === 'dashboard' ? 'active' : ''}" 
                        data-page="${item.id}">
                    <i class="${item.icon}"></i>
                    <span>${item.title.split(' ')[0]}</span>
                </button>
            `).join('');
        }
    }

    bindNavigationEvents(navItems) {
        // Desktop and mobile navigation
        document.querySelectorAll('.nav-item, .nav-item-mobile, .bottom-nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                if (page) {
                    this.navigateToPage(page);
                }
            });
        });
    }

    navigateToPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show target page
        const targetPage = document.getElementById(pageName);
        if (targetPage) {
            targetPage.classList.add('active');
            this.currentPage = pageName;
        }

        // Update active navigation items
        document.querySelectorAll('.nav-item, .nav-item-mobile, .bottom-nav-item').forEach(item => {
            item.classList.remove('active');
        });

        document.querySelectorAll(`[data-page="${pageName}"]`).forEach(item => {
            item.classList.add('active');
        });

        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            const pageTitles = {
                'dashboard': this.currentUser.role === 'employee' ? 'My Dashboard' : 'Dashboard',
                'employees': 'Employees',
                'attendance': this.currentUser.role === 'employee' ? 'My Attendance' : 'Attendance',
                'leaves': this.currentUser.role === 'employee' ? 'My Leaves' : 'Leave Management',
                'departments': 'Departments',
                'positions': 'Job Positions',
                'payroll': this.currentUser.role === 'employee' ? 'My Payroll' : 'Payroll'
            };
            pageTitle.textContent = pageTitles[pageName] || 'Dashboard';
        }

        // Load page-specific content
        this.loadPageContent(pageName);
        this.closeMobileSidebar();
    }

    updateUserInfo() {
        const userInitials = document.getElementById('userInitials');
        if (userInitials && this.currentUser) {
            userInitials.textContent = `${this.currentUser.first_name.charAt(0)}${this.currentUser.last_name.charAt(0)}`;
        }
    }

    loadPageContent(pageName) {
        switch (pageName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'employees':
                this.loadEmployees();
                break;
            case 'attendance':
                this.loadAttendance();
                break;
            case 'leaves':
                this.loadLeaves();
                break;
            case 'departments':
                this.loadDepartments();
                break;
            case 'positions':
                this.loadPositions();
                break;
            case 'payroll':
                this.loadPayroll();
                break;
            default:
                this.loadDashboard();
        }
    }

    // Dashboard
    loadDashboard() {
        this.renderMetricsCards();
        this.renderCharts();
    }

    renderMetricsCards() {
        const metricsGrid = document.getElementById('metricsGrid');
        if (!metricsGrid) return;

        let metrics = [];
        
        if (this.isAdminOrHR()) {
            const totalEmployees = this.users.filter(u => u.role === 'employee').length;
            const totalDepartments = this.departments.length;
            const pendingLeaves = this.leave_requests.filter(r => r.status === 'pending').length;
            const totalPayroll = this.payroll_records.reduce((sum, p) => sum + p.net_salary, 0);

            metrics = [
                {
                    value: totalEmployees,
                    label: 'Total Employees',
                    type: 'success',
                    change: '+2 this month'
                },
                {
                    value: totalDepartments,
                    label: 'Departments',
                    type: 'info',
                    change: 'Active'
                },
                {
                    value: pendingLeaves,
                    label: 'Pending Leaves',
                    type: 'warning',
                    change: 'Need approval'
                },
                {
                    value: `$${totalPayroll.toLocaleString()}`,
                    label: 'Monthly Payroll',
                    type: 'success',
                    change: 'Processed'
                }
            ];
        } else {
            // Employee dashboard metrics
            metrics = [
                {
                    value: '8.5h',
                    label: 'Today\'s Hours',
                    type: 'success',
                    change: 'On time'
                },
                {
                    value: '1',
                    label: 'Leave Requests',
                    type: 'info',
                    change: 'Approved'
                },
                {
                    value: '95%',
                    label: 'Attendance Rate',
                    type: 'success',
                    change: '+2%'
                },
                {
                    value: '$6,250',
                    label: 'Monthly Salary',
                    type: 'info',
                    change: 'Processed'
                }
            ];
        }

        metricsGrid.innerHTML = metrics.map(metric => `
            <div class="metric-card ${metric.type}">
                <div class="metric-value">${metric.value}</div>
                <div class="metric-label">${metric.label}</div>
                <div class="metric-change ${metric.change.includes('+') ? 'positive' : ''}">${metric.change}</div>
            </div>
        `).join('');
    }

    renderCharts() {
        setTimeout(() => {
            this.renderAttendanceChart();
            this.renderDepartmentChart();
        }, 100);
    }

    renderAttendanceChart() {
        const ctx = document.getElementById('attendanceChart');
        if (!ctx) return;

        if (this.charts.attendance) {
            this.charts.attendance.destroy();
        }

        this.charts.attendance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Present',
                    data: [95, 92, 88, 94, 89, 76, 45],
                    borderColor: '#1FB8CD',
                    backgroundColor: 'rgba(31, 184, 205, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Late',
                    data: [5, 8, 12, 6, 11, 24, 15],
                    borderColor: '#FFC185',
                    backgroundColor: 'rgba(255, 193, 133, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    renderDepartmentChart() {
        const ctx = document.getElementById('departmentChart');
        if (!ctx) return;

        if (this.charts.department) {
            this.charts.department.destroy();
        }

        this.charts.department = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.departments.map(d => d.name),
                datasets: [{
                    data: this.departments.map(d => d.employee_count),
                    backgroundColor: [
                        '#1FB8CD',
                        '#FFC185', 
                        '#B4413C',
                        '#ECEBD5',
                        '#5D878F'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    // Employee Management
    loadEmployees() {
        this.populateDropdowns();
        this.renderEmployees();
    }

    renderEmployees() {
        const tableBody = document.getElementById('employeesTableBody');
        if (!tableBody) return;

        let displayUsers = this.users;
        
        // Filter for employee role
        if (this.currentUser.role === 'employee') {
            displayUsers = this.users.filter(user => user.id === this.currentUser.id);
        }

        tableBody.innerHTML = displayUsers.map(user => {
            const employee = this.employees.find(e => e.user_id === user.id);
            const department = employee ? this.departments.find(d => d.id === employee.department) : null;
            const position = employee ? this.job_positions.find(p => p.id === employee.position) : null;

            return `
                <tr>
                    <td>
                        <div class="table-employee">
                            <div class="employee-avatar">
                                ${user.first_name.charAt(0)}${user.last_name.charAt(0)}
                            </div>
                            <div class="table-employee-info">
                                <div class="table-employee-name">${user.first_name} ${user.last_name}</div>
                                <div class="table-employee-id">${user.email}</div>
                            </div>
                        </div>
                    </td>
                    <td><span class="status ${user.role}">${this.capitalize(user.role)}</span></td>
                    <td>${department ? department.name : 'N/A'}</td>
                    <td>${position ? position.title : 'N/A'}</td>
                    <td><span class="status ${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn-action" onclick="app.viewUser(${user.id})">View</button>
                        ${this.isAdminOrHR() ? `<button class="btn-action btn-primary" onclick="app.editUser(${user.id})">Edit</button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Attendance Management
    loadAttendance() {
        this.setTodayDate('attendanceDate');
        this.renderAttendance();
    }

    renderAttendance() {
        const tableBody = document.getElementById('attendanceTableBody');
        if (!tableBody) return;

        let records = this.attendance_records;
        
        if (this.currentUser.role === 'employee') {
            const myEmployee = this.employees.find(e => e.user_id === this.currentUser.id);
            records = records.filter(r => r.employee_id === myEmployee?.id);
        }

        tableBody.innerHTML = records.map(record => {
            const employee = this.employees.find(e => e.id === record.employee_id);
            const user = employee ? this.users.find(u => u.id === employee.user_id) : null;
            const department = employee ? this.departments.find(d => d.id === employee.department) : null;

            return `
                <tr>
                    <td>
                        <div class="table-employee">
                            <div class="employee-avatar">
                                ${user?.first_name.charAt(0)}${user?.last_name.charAt(0)}
                            </div>
                            <div class="table-employee-info">
                                <div class="table-employee-name">${user?.first_name} ${user?.last_name}</div>
                                <div class="table-employee-id">${employee?.employee_id}</div>
                            </div>
                        </div>
                    </td>
                    <td>${this.formatDate(record.date)}</td>
                    <td>${this.formatTime(record.check_in_time)}</td>
                    <td>${record.check_out_time ? this.formatTime(record.check_out_time) : '-'}</td>
                    <td>${record.work_hours}h</td>
                    <td>
                        <span class="status ${record.is_absent ? 'absent' : record.is_late ? 'late' : 'present'}">
                            ${record.is_absent ? 'Absent' : record.is_late ? 'Late' : 'Present'}
                        </span>
                    </td>
                    <td>
                        <button class="btn-action" onclick="app.viewAttendance(${record.id})">View</button>
                        ${this.isAdminOrHR() ? `<button class="btn-action btn-primary" onclick="app.editAttendance(${record.id})">Edit</button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Leave Management
    loadLeaves() {
        this.renderLeaves();
    }

    renderLeaves() {
        const tableBody = document.getElementById('leavesTableBody');
        if (!tableBody) return;

        let requests = this.leave_requests;
        
        if (this.currentUser.role === 'employee') {
            const myEmployee = this.employees.find(e => e.user_id === this.currentUser.id);
            requests = requests.filter(r => r.employee_id === myEmployee?.id);
        }

        tableBody.innerHTML = requests.map(request => {
            const employee = this.employees.find(e => e.id === request.employee_id);
            const user = employee ? this.users.find(u => u.id === employee.user_id) : null;

            return `
                <tr>
                    <td>
                        <div class="table-employee">
                            <div class="employee-avatar">
                                ${user?.first_name.charAt(0)}${user?.last_name.charAt(0)}
                            </div>
                            <div class="table-employee-info">
                                <div class="table-employee-name">${user?.first_name} ${user?.last_name}</div>
                                <div class="table-employee-id">${employee?.employee_id}</div>
                            </div>
                        </div>
                    </td>
                    <td><span class="leave-type-badge">${this.capitalize(request.leave_type)}</span></td>
                    <td>${this.formatDate(request.start_date)}</td>
                    <td>${this.formatDate(request.end_date)}</td>
                    <td>${request.days_requested} day${request.days_requested > 1 ? 's' : ''}</td>
                    <td><span class="status ${request.status}">${this.capitalize(request.status)}</span></td>
                    <td>
                        ${request.status === 'pending' && this.isAdminOrHR() ? `
                            <button class="btn-action btn-primary" onclick="app.approveLeave(${request.id})">Approve</button>
                            <button class="btn-action btn-danger" onclick="app.rejectLeave(${request.id})">Reject</button>
                        ` : `
                            <button class="btn-action" onclick="app.viewLeave(${request.id})">View</button>
                        `}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Department Management
    loadDepartments() {
        this.renderDepartments();
    }

    renderDepartments() {
        const grid = document.getElementById('departmentsGrid');
        if (!grid) return;

        const departmentIcons = {
            'Human Resources': 'bi-people',
            'Engineering': 'bi-code-slash',
            'Sales': 'bi-graph-up',
            'Marketing': 'bi-megaphone',
            'Finance': 'bi-calculator'
        };

        grid.innerHTML = this.departments.map(department => `
            <div class="department-card">
                <div class="department-header">
                    <h3 class="department-name">${department.name}</h3>
                    <div class="department-icon">
                        <i class="${departmentIcons[department.name] || 'bi-building'}"></i>
                    </div>
                </div>
                <div class="department-budget">$${department.budget.toLocaleString()}</div>
                <div class="department-description">${department.description}</div>
                <div class="mt-16">
                    <button class="btn btn--outline btn--sm" onclick="app.viewDepartment(${department.id})">View Details</button>
                    ${this.isAdminOrHR() ? `<button class="btn btn--primary btn--sm" onclick="app.editDepartment(${department.id})">Edit</button>` : ''}
                </div>
            </div>
        `).join('');
    }

    // Job Positions
    loadPositions() {
        this.renderPositions();
    }

    renderPositions() {
        const tableBody = document.getElementById('positionsTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = this.job_positions.map(position => {
            const department = this.departments.find(d => d.id === position.department);

            return `
                <tr>
                    <td>${position.title}</td>
                    <td>${department ? department.name : 'N/A'}</td>
                    <td>$${position.min_salary.toLocaleString()} - $${position.max_salary.toLocaleString()}</td>
                    <td><span class="status ${position.is_active ? 'active' : 'inactive'}">${position.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn-action" onclick="app.viewPosition(${position.id})">View</button>
                        ${this.isAdminOrHR() ? `<button class="btn-action btn-primary" onclick="app.editPosition(${position.id})">Edit</button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Payroll Management
    loadPayroll() {
        this.renderPayroll();
    }

    renderPayroll() {
        const tableBody = document.getElementById('payrollTableBody');
        if (!tableBody) return;

        let records = this.payroll_records;
        
        if (this.currentUser.role === 'employee') {
            const myEmployee = this.employees.find(e => e.user_id === this.currentUser.id);
            records = records.filter(r => r.employee_id === myEmployee?.id);
        }

        tableBody.innerHTML = records.map(record => {
            const employee = this.employees.find(e => e.id === record.employee_id);
            const user = employee ? this.users.find(u => u.id === employee.user_id) : null;

            return `
                <tr>
                    <td>
                        <div class="table-employee">
                            <div class="employee-avatar">
                                ${user?.first_name.charAt(0)}${user?.last_name.charAt(0)}
                            </div>
                            <div class="table-employee-info">
                                <div class="table-employee-name">${user?.first_name} ${user?.last_name}</div>
                                <div class="table-employee-id">${employee?.employee_id}</div>
                            </div>
                        </div>
                    </td>
                    <td>${this.formatDate(record.pay_period_start)} - ${this.formatDate(record.pay_period_end)}</td>
                    <td>$${record.base_salary.toLocaleString()}</td>
                    <td>$${record.net_salary.toLocaleString()}</td>
                    <td><span class="status ${record.status}">${this.capitalize(record.status)}</span></td>
                    <td>
                        <button class="btn-action" onclick="app.viewPayroll(${record.id})">View</button>
                        ${this.isAdminOrHR() && record.status !== 'paid' ? `<button class="btn-action btn-primary" onclick="app.processPayroll(${record.id})">Process</button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // MODAL HANDLERS - ALL SIX MODALS

    // MODAL 1: Add User
    openAddUserModal() {
        if (!this.isAdminOrHR()) {
            this.showError('Access denied. Only admins and HR can add users.');
            return;
        }
        
        this.populateRoleDropdown();
        this.showModal('addUserModal');
        document.getElementById('addUserForm').reset();
    }

    async handleAddUser(e) {
        e.preventDefault();
        
        if (!this.validateUserForm()) return;
        
        const formData = new FormData(e.target);
        const userData = {
            username: formData.get('username') || document.getElementById('userUsername').value,
            email: formData.get('email') || document.getElementById('userEmail').value,
            first_name: formData.get('first_name') || document.getElementById('userFirstName').value,
            last_name: formData.get('last_name') || document.getElementById('userLastName').value,
            phone_number: formData.get('phone') || document.getElementById('userPhone').value,
            role: formData.get('role') || document.getElementById('userRole').value,
            password: formData.get('password') || document.getElementById('userPassword').value,
            is_active: true
        };

        this.showButtonLoading('addUserForm');

        try {
            await this.simulateAjaxCall('/api/user/create/', 'POST', userData);
            
            // Add to local data
            const newId = Math.max(...this.users.map(u => u.id)) + 1;
            this.users.push({
                id: newId,
                ...userData
            });

            this.showSuccess('User created successfully!');
            this.closeModal('addUserModal');
            this.renderEmployees();
            
        } catch (error) {
            this.showError('Failed to create user. Please try again.');
        } finally {
            this.hideButtonLoading('addUserForm');
        }
    }

    // MODAL 2: Add Payroll
    openAddPayrollModal() {
        if (!this.isAdminOrHR()) {
            this.showError('Access denied. Only admins and HR can add payroll records.');
            return;
        }
        
        this.populateEmployeeDropdowns();
        this.populateApproverDropdowns();
        this.showModal('addPayrollModal');
        document.getElementById('addPayrollForm').reset();
        
        // Set default values
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('payrollPeriodStart').value = today;
        document.getElementById('payrollPeriodEnd').value = today;
    }

    async handleAddPayroll(e) {
        e.preventDefault();
        
        if (!this.validatePayrollForm()) return;
        
        const payrollData = {
            employee_id: parseInt(document.getElementById('payrollEmployee').value),
            pay_period_start: document.getElementById('payrollPeriodStart').value,
            pay_period_end: document.getElementById('payrollPeriodEnd').value,
            base_salary: parseFloat(document.getElementById('payrollBaseSalary').value),
            hours_worked: parseFloat(document.getElementById('payrollHoursWorked').value) || 0,
            overtime_hours: parseFloat(document.getElementById('payrollOvertimeHours').value) || 0,
            overtime_pay: parseFloat(document.getElementById('payrollOvertimePay').value) || 0,
            deductions: parseFloat(document.getElementById('payrollDeductions').value) || 0,
            bonuses: parseFloat(document.getElementById('payrollBonuses').value) || 0,
            net_salary: parseFloat(document.getElementById('payrollNetSalary').value),
            status: document.getElementById('payrollStatus').value,
            created_by: this.currentUser.id,
            approved_by: document.getElementById('payrollApprovedBy').value || null,
            approved_at: document.getElementById('payrollApprovedAt').value || null
        };

        this.showButtonLoading('addPayrollForm');

        try {
            await this.simulateAjaxCall('/api/payroll/create/', 'POST', payrollData);
            
            // Add to local data
            const newId = Math.max(...this.payroll_records.map(p => p.id)) + 1;
            this.payroll_records.push({
                id: newId,
                ...payrollData
            });

            this.showSuccess('Payroll record created successfully!');
            this.closeModal('addPayrollModal');
            this.renderPayroll();
            
        } catch (error) {
            this.showError('Failed to create payroll record. Please try again.');
        } finally {
            this.hideButtonLoading('addPayrollForm');
        }
    }

    // MODAL 3: Add Attendance
    openAddAttendanceModal() {
        if (!this.isAdminOrHR()) {
            this.showError('Access denied. Only admins and HR can add attendance records.');
            return;
        }
        
        this.populateEmployeeDropdowns();
        this.showModal('addAttendanceModal');
        document.getElementById('addAttendanceForm').reset();
        
        // Set today's date
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('attendanceRecordDate').value = today;
    }

    async handleAddAttendance(e) {
        e.preventDefault();
        
        if (!this.validateAttendanceForm()) return;
        
        const attendanceData = {
            employee_id: parseInt(document.getElementById('attendanceEmployee').value),
            date: document.getElementById('attendanceRecordDate').value,
            check_in_time: document.getElementById('attendanceCheckIn').value,
            check_out_time: document.getElementById('attendanceCheckOut').value || null,
            work_hours: parseFloat(document.getElementById('attendanceWorkHours').value) || 0,
            overtime_hours: parseFloat(document.getElementById('attendanceOvertimeHours').value) || 0,
            is_late: document.getElementById('attendanceIsLate').checked,
            is_absent: document.getElementById('attendanceIsAbsent').checked,
            notes: document.getElementById('attendanceNotes').value
        };

        this.showButtonLoading('addAttendanceForm');

        try {
            await this.simulateAjaxCall('/api/attendance/create/', 'POST', attendanceData);
            
            // Add to local data
            const newId = Math.max(...this.attendance_records.map(a => a.id)) + 1;
            this.attendance_records.push({
                id: newId,
                ...attendanceData
            });

            this.showSuccess('Attendance record created successfully!');
            this.closeModal('addAttendanceModal');
            this.renderAttendance();
            
        } catch (error) {
            this.showError('Failed to create attendance record. Please try again.');
        } finally {
            this.hideButtonLoading('addAttendanceForm');
        }
    }

    // MODAL 4: Add Department
    openAddDepartmentModal() {
        if (!this.isAdminOrHR()) {
            this.showError('Access denied. Only admins and HR can add departments.');
            return;
        }
        
        this.populateManagerDropdowns();
        this.showModal('addDepartmentModal');
        document.getElementById('addDepartmentForm').reset();
        document.getElementById('departmentIsActive').checked = true;
    }

    async handleAddDepartment(e) {
        e.preventDefault();
        
        if (!this.validateDepartmentForm()) return;
        
        const departmentData = {
            name: document.getElementById('departmentName').value,
            description: document.getElementById('departmentDescription').value,
            manager: document.getElementById('departmentManager').value || null,
            budget: parseFloat(document.getElementById('departmentBudget').value) || 0,
            is_active: document.getElementById('departmentIsActive').checked,
            employee_count: 0
        };

        this.showButtonLoading('addDepartmentForm');

        try {
            await this.simulateAjaxCall('/api/department/create/', 'POST', departmentData);
            
            // Add to local data
            const newId = Math.max(...this.departments.map(d => d.id)) + 1;
            this.departments.push({
                id: newId,
                ...departmentData
            });

            this.showSuccess('Department created successfully!');
            this.closeModal('addDepartmentModal');
            this.renderDepartments();
            
        } catch (error) {
            this.showError('Failed to create department. Please try again.');
        } finally {
            this.hideButtonLoading('addDepartmentForm');
        }
    }

    // MODAL 5: Add Leave Request
    openAddLeaveRequestModal() {
        this.populateLeaveRequestModal();
        this.showModal('addLeaveRequestModal');
        document.getElementById('addLeaveRequestForm').reset();
        
        // Role-based field configuration
        if (this.currentUser.role === 'employee') {
            // Employee can only create for themselves, status is always pending
            document.getElementById('leaveEmployeeRow').style.display = 'none';
            document.getElementById('leaveStatusGroup').style.display = 'none';
            document.getElementById('leaveApprovalSection').classList.add('hidden');
        } else {
            // HR/Admin can create for any employee and set status
            this.populateEmployeeDropdowns();
            this.populateApproverDropdowns();
            document.getElementById('leaveEmployeeRow').style.display = 'grid';
            document.getElementById('leaveStatusGroup').style.display = 'block';
        }
    }

    async handleAddLeaveRequest(e) {
        e.preventDefault();
        
        if (!this.validateLeaveRequestForm()) return;
        
        let employeeId;
        if (this.currentUser.role === 'employee') {
            const myEmployee = this.employees.find(emp => emp.user_id === this.currentUser.id);
            employeeId = myEmployee?.id;
        } else {
            employeeId = parseInt(document.getElementById('leaveEmployee').value);
        }

        const leaveData = {
            employee_id: employeeId,
            leave_type: document.getElementById('leaveType').value,
            start_date: document.getElementById('leaveStartDate').value,
            end_date: document.getElementById('leaveEndDate').value,
            days_requested: parseInt(document.getElementById('leaveDaysRequested').value),
            reason: document.getElementById('leaveReason').value,
            status: this.currentUser.role === 'employee' ? 'pending' : document.getElementById('leaveStatus').value,
            approved_by: document.getElementById('leaveApprovedBy').value || null,
            approved_at: document.getElementById('leaveApprovedAt').value || null,
            rejection_reason: document.getElementById('leaveRejectionReason').value || ''
        };

        this.showButtonLoading('addLeaveRequestForm');

        try {
            await this.simulateAjaxCall('/api/leave-request/create/', 'POST', leaveData);
            
            // Add to local data
            const newId = Math.max(...this.leave_requests.map(l => l.id)) + 1;
            this.leave_requests.push({
                id: newId,
                ...leaveData
            });

            this.showSuccess('Leave request submitted successfully!');
            this.closeModal('addLeaveRequestModal');
            this.renderLeaves();
            
        } catch (error) {
            this.showError('Failed to submit leave request. Please try again.');
        } finally {
            this.hideButtonLoading('addLeaveRequestForm');
        }
    }

    // MODAL 6: Add Job Position
    openAddJobPositionModal() {
        if (!this.isAdminOrHR()) {
            this.showError('Access denied. Only admins and HR can add job positions.');
            return;
        }
        
        this.populateDepartmentDropdowns();
        this.showModal('addJobPositionModal');
        document.getElementById('addJobPositionForm').reset();
        document.getElementById('positionIsActive').checked = true;
    }

    async handleAddJobPosition(e) {
        e.preventDefault();
        
        if (!this.validateJobPositionForm()) return;
        
        const positionData = {
            title: document.getElementById('positionTitle').value,
            department: parseInt(document.getElementById('positionDepartment').value),
            description: document.getElementById('positionDescription').value,
            requirements: document.getElementById('positionRequirements').value,
            min_salary: parseFloat(document.getElementById('positionMinSalary').value),
            max_salary: parseFloat(document.getElementById('positionMaxSalary').value),
            is_active: document.getElementById('positionIsActive').checked
        };

        this.showButtonLoading('addJobPositionForm');

        try {
            await this.simulateAjaxCall('/api/job-position/create/', 'POST', positionData);
            
            // Add to local data
            const newId = Math.max(...this.job_positions.map(p => p.id)) + 1;
            this.job_positions.push({
                id: newId,
                ...positionData
            });

            this.showSuccess('Job position created successfully!');
            this.closeModal('addJobPositionModal');
            this.renderPositions();
            
        } catch (error) {
            this.showError('Failed to create job position. Please try again.');
        } finally {
            this.hideButtonLoading('addJobPositionForm');
        }
    }

    // AUTO-CALCULATIONS

    calculateNetSalary() {
        const baseSalary = parseFloat(document.getElementById('payrollBaseSalary').value) || 0;
        const overtimePay = parseFloat(document.getElementById('payrollOvertimePay').value) || 0;
        const bonuses = parseFloat(document.getElementById('payrollBonuses').value) || 0;
        const deductions = parseFloat(document.getElementById('payrollDeductions').value) || 0;
        
        const netSalary = baseSalary + overtimePay + bonuses - deductions;
        document.getElementById('payrollNetSalary').value = netSalary.toFixed(2);
    }

    calculateWorkHours() {
        const checkIn = document.getElementById('attendanceCheckIn').value;
        const checkOut = document.getElementById('attendanceCheckOut').value;
        
        if (checkIn && checkOut) {
            const checkInTime = new Date(checkIn);
            const checkOutTime = new Date(checkOut);
            
            if (checkOutTime > checkInTime) {
                const diffMs = checkOutTime - checkInTime;
                const workHours = diffMs / (1000 * 60 * 60);
                const overtimeHours = Math.max(0, workHours - 8);
                
                document.getElementById('attendanceWorkHours').value = workHours.toFixed(2);
                document.getElementById('attendanceOvertimeHours').value = overtimeHours.toFixed(2);
            }
        }
    }

    calculateLeaveDays() {
        const startDate = document.getElementById('leaveStartDate').value;
        const endDate = document.getElementById('leaveEndDate').value;
        
        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            
            if (end >= start) {
                const diffTime = Math.abs(end - start);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
                document.getElementById('leaveDaysRequested').value = diffDays;
            }
        }
    }

    validateSalaryRange() {
        const minSalary = parseFloat(document.getElementById('positionMinSalary').value) || 0;
        const maxSalary = parseFloat(document.getElementById('positionMaxSalary').value) || 0;
        
        if (minSalary > maxSalary && maxSalary > 0) {
            this.showError('Maximum salary must be greater than minimum salary.');
            document.getElementById('positionMaxSalary').focus();
        }
    }

    // DROPDOWN POPULATION

    populateDropdowns() {
        this.populateDepartmentDropdowns();
        this.populateEmployeeDropdowns();
        this.populateApproverDropdowns();
        this.populateManagerDropdowns();
        this.populateRoleDropdown();
    }

    populateDepartmentDropdowns() {
        const selectors = ['departmentFilter', 'positionDepartment', 'departmentManager'];
        selectors.forEach(selector => {
            const element = document.getElementById(selector);
            if (element && selector !== 'departmentFilter') {
                const options = this.departments.map(dept => 
                    `<option value="${dept.id}">${dept.name}</option>`
                ).join('');
                
                if (selector === 'departmentManager') {
                    element.innerHTML = '<option value="">Select Manager</option>' + options;
                } else {
                    element.innerHTML = '<option value="">Select Department</option>' + options;
                }
            } else if (element && selector === 'departmentFilter') {
                const options = this.departments.map(dept => 
                    `<option value="${dept.id}">${dept.name}</option>`
                ).join('');
                element.innerHTML = '<option value="">All Departments</option>' + options;
            }
        });
    }

    populateEmployeeDropdowns() {
        const selectors = ['payrollEmployee', 'attendanceEmployee', 'leaveEmployee'];
        const employees = this.getFilteredEmployees();
        
        selectors.forEach(selector => {
            const element = document.getElementById(selector);
            if (element) {
                const options = employees.map(emp => {
                    const user = this.users.find(u => u.id === emp.user_id);
                    return `<option value="${emp.id}">${user?.first_name} ${user?.last_name} (${emp.employee_id})</option>`;
                }).join('');
                element.innerHTML = '<option value="">Select Employee</option>' + options;
            }
        });
    }

    populateApproverDropdowns() {
        const selectors = ['payrollApprovedBy', 'leaveApprovedBy'];
        const approvers = this.users.filter(user => user.role === 'admin' || user.role === 'hr');
        
        selectors.forEach(selector => {
            const element = document.getElementById(selector);
            if (element) {
                const options = approvers.map(user => 
                    `<option value="${user.id}">${user.first_name} ${user.last_name}</option>`
                ).join('');
                element.innerHTML = '<option value="">Select Approver</option>' + options;
            }
        });
    }

    populateManagerDropdowns() {
        const element = document.getElementById('departmentManager');
        if (element) {
            const managers = this.users.filter(user => user.role === 'admin' || user.role === 'hr');
            const options = managers.map(user => 
                `<option value="${user.id}">${user.first_name} ${user.last_name}</option>`
            ).join('');
            element.innerHTML = '<option value="">Select Manager</option>' + options;
        }
    }

    populateRoleDropdown() {
        const element = document.getElementById('userRole');
        if (element) {
            let roles = [];
            
            if (this.currentUser.role === 'admin') {
                roles = [
                    { value: 'admin', label: 'Administrator' },
                    { value: 'hr', label: 'HR Manager' },
                    { value: 'employee', label: 'Employee' }
                ];
            } else if (this.currentUser.role === 'hr') {
                roles = [
                    { value: 'hr', label: 'HR Manager' },
                    { value: 'employee', label: 'Employee' }
                ];
            }
            
            const options = roles.map(role => 
                `<option value="${role.value}">${role.label}</option>`
            ).join('');
            element.innerHTML = '<option value="">Select Role</option>' + options;
        }
    }

    populateLeaveRequestModal() {
        // This is called when opening the leave request modal
        // Additional setup can be done here
    }

    // FORM VALIDATIONS

    validateUserForm() {
        const username = document.getElementById('userUsername').value;
        const email = document.getElementById('userEmail').value;
        const password = document.getElementById('userPassword').value;
        const passwordConfirm = document.getElementById('userPasswordConfirm').value;
        
        if (!username || !email || !password || !passwordConfirm) {
            this.showError('Please fill in all required fields.');
            return false;
        }
        
        if (password !== passwordConfirm) {
            this.showError('Passwords do not match.');
            return false;
        }
        
        if (this.users.some(u => u.username === username)) {
            this.showError('Username already exists.');
            return false;
        }
        
        if (this.users.some(u => u.email === email)) {
            this.showError('Email already exists.');
            return false;
        }
        
        return true;
    }

    validatePayrollForm() {
        const periodStart = document.getElementById('payrollPeriodStart').value;
        const periodEnd = document.getElementById('payrollPeriodEnd').value;
        const baseSalary = document.getElementById('payrollBaseSalary').value;
        
        if (!periodStart || !periodEnd || !baseSalary) {
            this.showError('Please fill in all required fields.');
            return false;
        }
        
        if (new Date(periodEnd) < new Date(periodStart)) {
            this.showError('Pay period end date must be after start date.');
            return false;
        }
        
        return true;
    }

    validateAttendanceForm() {
        const employeeId = document.getElementById('attendanceEmployee').value;
        const date = document.getElementById('attendanceRecordDate').value;
        const checkIn = document.getElementById('attendanceCheckIn').value;
        
        if (!employeeId || !date || !checkIn) {
            this.showError('Please fill in all required fields.');
            return false;
        }
        
        const checkOut = document.getElementById('attendanceCheckOut').value;
        if (checkOut && new Date(checkOut) <= new Date(checkIn)) {
            this.showError('Check out time must be after check in time.');
            return false;
        }
        
        return true;
    }

    validateDepartmentForm() {
        const name = document.getElementById('departmentName').value;
        
        if (!name) {
            this.showError('Please enter a department name.');
            return false;
        }
        
        if (this.departments.some(d => d.name.toLowerCase() === name.toLowerCase())) {
            this.showError('Department name already exists.');
            return false;
        }
        
        const budget = document.getElementById('departmentBudget').value;
        if (budget && parseFloat(budget) < 0) {
            this.showError('Budget must be a positive number.');
            return false;
        }
        
        return true;
    }

    validateLeaveRequestForm() {
        const leaveType = document.getElementById('leaveType').value;
        const startDate = document.getElementById('leaveStartDate').value;
        const endDate = document.getElementById('leaveEndDate').value;
        const reason = document.getElementById('leaveReason').value;
        
        if (!leaveType || !startDate || !endDate || !reason) {
            this.showError('Please fill in all required fields.');
            return false;
        }
        
        if (new Date(endDate) < new Date(startDate)) {
            this.showError('End date must be after start date.');
            return false;
        }
        
        return true;
    }

    validateJobPositionForm() {
        const title = document.getElementById('positionTitle').value;
        const department = document.getElementById('positionDepartment').value;
        const minSalary = parseFloat(document.getElementById('positionMinSalary').value);
        const maxSalary = parseFloat(document.getElementById('positionMaxSalary').value);
        
        if (!title || !department || !minSalary || !maxSalary) {
            this.showError('Please fill in all required fields.');
            return false;
        }
        
        if (maxSalary <= minSalary) {
            this.showError('Maximum salary must be greater than minimum salary.');
            return false;
        }
        
        return true;
    }

    // HELPER METHODS

    isAdminOrHR() {
        return this.currentUser && (this.currentUser.role === 'admin' || this.currentUser.role === 'hr');
    }

    getFilteredEmployees() {
        if (this.currentUser.role === 'admin') {
            return this.employees;
        } else if (this.currentUser.role === 'hr') {
            // HR cannot see admin users in employee dropdowns
            const nonAdminUsers = this.users.filter(u => u.role !== 'admin');
            return this.employees.filter(emp => 
                nonAdminUsers.some(u => u.id === emp.user_id)
            );
        }
        return [];
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    showButtonLoading(formId) {
        const form = document.getElementById(formId);
        const submitBtn = form?.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        }
    }

    hideButtonLoading(formId) {
        const form = document.getElementById(formId);
        const submitBtn = form?.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }

    async simulateAjaxCall(endpoint, method, data) {
        // Simulate AJAX call with realistic delay
        await this.simulateAjaxDelay();
        
        // Simulate success/failure based on endpoint
        if (Math.random() < 0.95) { // 95% success rate
            return { success: true, data: data };
        } else {
            throw new Error('Simulated network error');
        }
    }

    async simulateAjaxDelay() {
        const delay = Math.random() * 1000 + 500; // 500-1500ms delay
        return new Promise(resolve => setTimeout(resolve, delay));
    }

    setTodayDate(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const today = new Date().toISOString().split('T')[0];
            element.value = today;
        }
    }

    capitalize(str) {
        return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString();
    }

    formatTime(timeString) {
        if (!timeString) return 'N/A';
        return new Date(timeString).toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    // Mobile sidebar
    toggleMobileSidebar() {
        const sidebar = document.getElementById('sidebarMobile');
        const overlay = document.getElementById('sidebarOverlay');
        
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    }

    closeMobileSidebar() {
        const sidebar = document.getElementById('sidebarMobile');
        const overlay = document.getElementById('sidebarOverlay');
        
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
    }

    // Notifications
    updateNotifications() {
        const count = document.getElementById('notificationCount');
        if (count) {
            count.textContent = '3';
            count.style.display = 'flex';
        }
    }

    toggleNotifications() {
        const panel = document.getElementById('notificationPanel');
        if (panel.classList.contains('show')) {
            this.closeNotifications();
        } else {
            this.showNotifications();
        }
    }

    showNotifications() {
        const panel = document.getElementById('notificationPanel');
        panel.classList.add('show');
        this.renderNotifications();
    }

    closeNotifications() {
        const panel = document.getElementById('notificationPanel');
        panel.classList.remove('show');
    }

    renderNotifications() {
        const list = document.getElementById('notificationList');
        if (list) {
            list.innerHTML = `
                <div class="notification-item">
                    <div class="notification-title">Leave Request Pending</div>
                    <div class="notification-message">John Doe has submitted a leave request that requires approval.</div>
                    <div class="notification-time">2 hours ago</div>
                </div>
                <div class="notification-item">
                    <div class="notification-title">Payroll Processing Complete</div>
                    <div class="notification-message">March 2024 payroll has been successfully processed.</div>
                    <div class="notification-time">1 day ago</div>
                </div>
                <div class="notification-item">
                    <div class="notification-title">New Employee Added</div>
                    <div class="notification-message">Alice Smith has been added to the system.</div>
                    <div class="notification-time">3 days ago</div>
                </div>
            `;
        }
    }

    // Filter methods
    filterEmployees() {
        // This would typically filter the displayed employees
        this.renderEmployees();
    }

    filterLeaves() {
        // This would typically filter the displayed leave requests
        this.renderLeaves();
    }

    filterPayroll() {
        // This would typically filter the displayed payroll records
        this.renderPayroll();
    }

    // Action methods (placeholders for actual functionality)
    viewUser(userId) {
        this.showInfo(`Viewing user details for ID: ${userId}`);
    }

    editUser(userId) {
        this.showInfo(`Edit user functionality for ID: ${userId} would open here`);
    }

    viewAttendance(recordId) {
        this.showInfo(`Viewing attendance record for ID: ${recordId}`);
    }

    editAttendance(recordId) {
        this.showInfo(`Edit attendance functionality for ID: ${recordId} would open here`);
    }

    approveLeave(leaveId) {
        const leave = this.leave_requests.find(l => l.id === leaveId);
        if (leave) {
            leave.status = 'approved';
            leave.approved_by = this.currentUser.id;
            leave.approved_at = new Date().toISOString();
            this.renderLeaves();
            this.showSuccess('Leave request approved successfully!');
        }
    }

    rejectLeave(leaveId) {
        const leave = this.leave_requests.find(l => l.id === leaveId);
        if (leave) {
            leave.status = 'rejected';
            leave.approved_by = this.currentUser.id;
            leave.approved_at = new Date().toISOString();
            this.renderLeaves();
            this.showInfo('Leave request rejected.');
        }
    }

    viewLeave(leaveId) {
        this.showInfo(`Viewing leave request details for ID: ${leaveId}`);
    }

    viewDepartment(departmentId) {
        this.showInfo(`Viewing department details for ID: ${departmentId}`);
    }

    editDepartment(departmentId) {
        this.showInfo(`Edit department functionality for ID: ${departmentId} would open here`);
    }

    viewPosition(positionId) {
        this.showInfo(`Viewing position details for ID: ${positionId}`);
    }

    editPosition(positionId) {
        this.showInfo(`Edit position functionality for ID: ${positionId} would open here`);
    }

    viewPayroll(recordId) {
        this.showInfo(`Viewing payroll record for ID: ${recordId}`);
    }

    processPayroll(recordId) {
        const record = this.payroll_records.find(r => r.id === recordId);
        if (record) {
            record.status = 'paid';
            this.renderPayroll();
            this.showSuccess('Payroll record processed successfully!');
        }
    }

    // Toast notification methods
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        document.querySelectorAll('.toast-notification').forEach(toast => toast.remove());

        const notification = document.createElement('div');
        notification.className = `toast-notification ${type}`;
        notification.innerHTML = `
            <div class="toast-content">
                <i class="bi bi-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'x-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AttendixApp();
});