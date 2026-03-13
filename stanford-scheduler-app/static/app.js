// Stanford Course Scheduler - Frontend
(function () {
    "use strict";

    // State
    let allCourses = [];
    let displayedCourses = [];
    let mySchedule = JSON.parse(localStorage.getItem("mySchedule") || "[]");
    let recommendations = {};
    let activeFilters = { dept: null, days: null };

    // DOM refs
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");
    const courseList = document.getElementById("courseList");
    const resultCount = document.getElementById("resultCount");
    const scheduleCourses = document.getElementById("scheduleCourses");
    const totalUnitsEl = document.getElementById("totalUnits");
    const courseCountEl = document.getElementById("courseCount");
    const conflictBanner = document.getElementById("conflictBanner");
    const conflictDetails = document.getElementById("conflictDetails");
    const calBody = document.getElementById("calBody");
    const recList = document.getElementById("recommendationsList");

    // Init
    async function init() {
        courseList.innerHTML = '<div class="loading">Loading courses</div>';

        const [coursesRes, recRes] = await Promise.all([
            fetch("/api/courses"),
            fetch("/api/recommendations"),
        ]);

        allCourses = await coursesRes.json();
        recommendations = await recRes.json();

        displayedCourses = allCourses;
        renderCourses(allCourses);
        renderSchedule();
        renderRecommendations();
        setupEvents();
    }

    // Events
    function setupEvents() {
        searchBtn.addEventListener("click", doSearch);
        searchInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") doSearch();
        });

        // Filter chips
        document.querySelectorAll(".chip[data-dept]").forEach((chip) => {
            chip.addEventListener("click", () => {
                if (chip.classList.contains("active")) {
                    chip.classList.remove("active");
                    activeFilters.dept = null;
                } else {
                    document.querySelectorAll(".chip[data-dept]").forEach((c) => c.classList.remove("active"));
                    chip.classList.add("active");
                    activeFilters.dept = chip.dataset.dept;
                }
                doSearch();
            });
        });

        document.querySelectorAll(".chip[data-days]").forEach((chip) => {
            chip.addEventListener("click", () => {
                if (chip.classList.contains("active")) {
                    chip.classList.remove("active");
                    activeFilters.days = null;
                } else {
                    document.querySelectorAll(".chip[data-days]").forEach((c) => c.classList.remove("active"));
                    chip.classList.add("active");
                    activeFilters.days = chip.dataset.days;
                }
                doSearch();
            });
        });

        document.getElementById("clearFilters").addEventListener("click", () => {
            document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
            activeFilters = { dept: null, days: null };
            searchInput.value = "";
            doSearch();
        });

        // Tabs
        document.querySelectorAll(".tab").forEach((tab) => {
            tab.addEventListener("click", () => {
                document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
                document.querySelectorAll(".tab-content").forEach((tc) => tc.classList.remove("active"));
                tab.classList.add("active");
                document.getElementById(tab.dataset.tab + "Tab").classList.add("active");
            });
        });
    }

    // Search
    async function doSearch() {
        const q = searchInput.value.trim();
        const params = new URLSearchParams();
        if (q) params.set("q", q);
        if (activeFilters.dept) params.set("dept", activeFilters.dept);
        if (activeFilters.days) params.set("days", activeFilters.days);

        courseList.innerHTML = '<div class="loading">Searching</div>';

        const res = await fetch("/api/search?" + params.toString());
        const results = await res.json();
        displayedCourses = results;
        renderCourses(results);

        // Switch to search tab
        document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach((tc) => tc.classList.remove("active"));
        document.querySelector('.tab[data-tab="search"]').classList.add("active");
        document.getElementById("searchTab").classList.add("active");
    }

    // Render course cards
    function renderCourses(courses) {
        resultCount.textContent = `${courses.length} course${courses.length !== 1 ? "s" : ""} found`;

        if (courses.length === 0) {
            courseList.innerHTML = '<div class="empty-schedule"><p>No courses match your search.</p><p class="hint">Try a different query or clear filters.</p></div>';
            return;
        }

        courseList.innerHTML = courses.map((c) => courseCardHTML(c)).join("");

        // Attach button handlers
        courseList.querySelectorAll(".btn-add").forEach((btn) => {
            btn.addEventListener("click", () => addToSchedule(btn.dataset.code));
        });
        courseList.querySelectorAll(".btn-remove").forEach((btn) => {
            btn.addEventListener("click", () => removeFromSchedule(btn.dataset.code));
        });
    }

    function courseCardHTML(course, showWhy = false) {
        const inSchedule = mySchedule.some((c) => c.code === course.code);
        const btnHTML = inSchedule
            ? `<button class="btn-remove" data-code="${esc(course.code)}">Remove</button>`
            : `<button class="btn-add" data-code="${esc(course.code)}">+ Add to Schedule</button>`;

        const whyHTML = showWhy && course.why
            ? `<div class="rec-why">💡 ${esc(course.why)}</div>`
            : "";

        return `
            <div class="course-card" data-code="${esc(course.code)}">
                <div class="course-card-header">
                    <span class="course-code">${esc(course.code)}</span>
                    <span class="course-units">${esc(course.units || "—")} units</span>
                </div>
                <div class="course-title">${esc(course.title)}</div>
                <div class="course-meta">
                    ${course.schedule ? `<span class="meta-schedule">${esc(course.schedule)}</span>` : ""}
                    ${course.instructor ? `<span class="meta-instructor">${esc(course.instructor)}</span>` : ""}
                    ${course.department ? `<span class="meta-dept">${esc(course.department)}</span>` : ""}
                </div>
                <div class="course-desc">${esc(course.description)}</div>
                ${whyHTML}
                <div class="course-actions">${btnHTML}</div>
            </div>
        `;
    }

    // Recommendations
    function renderRecommendations() {
        let html = "";
        for (const [key, cat] of Object.entries(recommendations)) {
            html += `
                <div class="rec-category">
                    <div class="rec-category-header">${cat.emoji} ${esc(cat.label)}</div>
                    <div class="rec-category-desc">${esc(cat.description)}</div>
                    ${cat.courses.map((c) => courseCardHTML(c, true)).join("")}
                </div>
            `;
        }
        recList.innerHTML = html;

        // Attach button handlers
        recList.querySelectorAll(".btn-add").forEach((btn) => {
            btn.addEventListener("click", () => addToSchedule(btn.dataset.code));
        });
        recList.querySelectorAll(".btn-remove").forEach((btn) => {
            btn.addEventListener("click", () => removeFromSchedule(btn.dataset.code));
        });
    }

    // Schedule management
    function addToSchedule(code) {
        if (mySchedule.some((c) => c.code === code)) return;
        const course = allCourses.find((c) => c.code === code);
        if (!course) return;
        mySchedule.push(course);
        saveSchedule();
        renderSchedule();
        renderCourses(displayedCourses);
        renderRecommendations();
    }

    function removeFromSchedule(code) {
        mySchedule = mySchedule.filter((c) => c.code !== code);
        saveSchedule();
        renderSchedule();
        renderCourses(displayedCourses);
        renderRecommendations();
    }

    function saveSchedule() {
        localStorage.setItem("mySchedule", JSON.stringify(mySchedule));
    }

    function renderSchedule() {
        // Update header counts
        let totalUnits = 0;
        mySchedule.forEach((c) => {
            const u = c.units || "0";
            if (u.includes("-")) {
                totalUnits += parseInt(u.split("-")[1]);
            } else {
                totalUnits += parseInt(u) || 0;
            }
        });
        totalUnitsEl.textContent = totalUnits;
        courseCountEl.textContent = mySchedule.length;

        // Render schedule items
        if (mySchedule.length === 0) {
            scheduleCourses.innerHTML = '<div class="empty-schedule"><p>No courses added yet.</p><p class="hint">Search and click "Add to Schedule" to build your plan.</p></div>';
            conflictBanner.style.display = "none";
        } else {
            scheduleCourses.innerHTML = mySchedule
                .map(
                    (c) => `
                <div class="schedule-item">
                    <div class="schedule-item-info">
                        <div class="schedule-item-code">${esc(c.code)}</div>
                        <div class="schedule-item-title">${esc(c.title)}</div>
                        <div class="schedule-item-time">${esc(c.schedule || "TBD")}</div>
                    </div>
                    <button class="btn-remove" data-code="${esc(c.code)}">✕</button>
                </div>
            `
                )
                .join("");

            scheduleCourses.querySelectorAll(".btn-remove").forEach((btn) => {
                btn.addEventListener("click", () => removeFromSchedule(btn.dataset.code));
            });
        }

        checkConflicts();
        renderCalendar();
    }

    // Conflict checking
    async function checkConflicts() {
        if (mySchedule.length < 2) {
            conflictBanner.style.display = "none";
            return;
        }

        const res = await fetch("/api/check-conflicts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(mySchedule),
        });
        const data = await res.json();

        if (data.conflicts && data.conflicts.length > 0) {
            conflictBanner.style.display = "block";
            conflictDetails.innerHTML = data.conflicts
                .map((c) => `<div>• ${esc(c.detail)}</div>`)
                .join("");
        } else {
            conflictBanner.style.display = "none";
        }
    }

    // Calendar rendering
    function renderCalendar() {
        const START_HOUR = 8; // 8 AM
        const END_HOUR = 19; // 7 PM
        const HOUR_HEIGHT = 44; // px per hour
        const totalHeight = (END_HOUR - START_HOUR) * HOUR_HEIGHT;

        // Build time labels column
        let timesHTML = '<div class="cal-time-col" style="grid-row: 1; grid-column: 1;">';
        for (let h = START_HOUR; h <= END_HOUR; h++) {
            const top = (h - START_HOUR) * HOUR_HEIGHT;
            const label = h <= 12 ? `${h}AM` : `${h - 12}PM`;
            timesHTML += `<div class="cal-time-label" style="position:absolute;top:${top}px;right:4px;"><span>${h === 12 ? "12PM" : label}</span></div>`;
        }
        timesHTML += "</div>";

        const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
        let colsHTML = "";

        days.forEach((day, di) => {
            let colContent = "";

            // Hour lines
            for (let h = START_HOUR; h <= END_HOUR; h++) {
                const top = (h - START_HOUR) * HOUR_HEIGHT;
                colContent += `<div class="cal-hour-line" style="top:${top}px"></div>`;
            }

            // Events for this day
            mySchedule.forEach((course, ci) => {
                const slots = parseTimeSlots(course.schedule || "");
                slots.forEach((slot) => {
                    if (slot.day !== day) return;
                    const top = ((slot.startMin - START_HOUR * 60) / 60) * HOUR_HEIGHT;
                    const height = ((slot.endMin - slot.startMin) / 60) * HOUR_HEIGHT;
                    if (top < 0 || top > totalHeight) return;
                    const colorClass = `cal-color-${ci % 8}`;
                    colContent += `<div class="cal-event ${colorClass}" style="top:${top}px;height:${Math.max(height, 18)}px;" title="${esc(course.code)}: ${esc(course.title)}">
                        <div>${esc(course.code)}</div>
                    </div>`;
                });
            });

            colsHTML += `<div class="cal-column" style="grid-row:1;grid-column:${di + 2};height:${totalHeight}px;position:relative;">${colContent}</div>`;
        });

        calBody.style.minHeight = totalHeight + "px";
        calBody.innerHTML = `<div style="grid-row:1;grid-column:1;position:relative;height:${totalHeight}px;border-right:1px solid var(--border);">${timesHTML}</div>${colsHTML}`;
    }

    function parseTimeSlots(schedule) {
        const slots = [];
        if (!schedule) return slots;

        const days = schedule.match(/(Mon|Tue|Wed|Thu|Fri|Sat|Sun)/g);
        // Try "1:30 PM - 2:50 PM" first, then "1:30-2:50 PM"
        let sh, sm, sp, eh, em, ep;
        let timeMatch = schedule.match(/(\d{1,2}):(\d{2})\s*(AM|PM)\s*[-–]\s*(\d{1,2}):(\d{2})\s*(AM|PM)/i);
        if (timeMatch) {
            sh = parseInt(timeMatch[1]); sm = parseInt(timeMatch[2]); sp = timeMatch[3].toUpperCase();
            eh = parseInt(timeMatch[4]); em = parseInt(timeMatch[5]); ep = timeMatch[6].toUpperCase();
        } else {
            timeMatch = schedule.match(/(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})\s*(AM|PM)/i);
            if (!timeMatch) return slots;
            sh = parseInt(timeMatch[1]); sm = parseInt(timeMatch[2]); sp = timeMatch[5].toUpperCase();
            eh = parseInt(timeMatch[3]); em = parseInt(timeMatch[4]); ep = timeMatch[5].toUpperCase();
        }
        if (!days) return slots;

        const startMin = (sh % 12) * 60 + sm + (sp === "PM" ? 720 : 0);
        const endMin = (eh % 12) * 60 + em + (ep === "PM" ? 720 : 0);

        days.forEach((day) => {
            slots.push({ day, startMin, endMin });
        });

        return slots;
    }

    // Utility
    function esc(str) {
        if (!str) return "";
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    // Go
    init();
})();
