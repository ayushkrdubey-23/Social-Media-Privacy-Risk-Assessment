"use strict";

/*
 * Frontend application for the
 * Social Media Privacy Risk Assessment Framework.
 *
 * This file:
 * - checks backend health,
 * - loads aggregate dashboard statistics,
 * - renders charts,
 * - renders category statistics.
 *
 * It does not collect direct personal information.
 */

const API_BASE_URL = "http://127.0.0.1:5000";

let riskDistributionChart = null;
let categoryScoreChart = null;


function getElement(id) {
    return document.getElementById(id);
}


function setApiStatus(isOnline, message) {
    const dot = getElement("api-status-dot");
    const text = getElement("api-status-text");

    if (!dot || !text) {
        return;
    }

    dot.classList.remove(
        "online",
        "offline"
    );

    dot.classList.add(
        isOnline ? "online" : "offline"
    );

    text.textContent = message;
}


function setDashboardMessage(
    message,
    isError = false
) {
    const element = getElement(
        "dashboard-message"
    );

    if (!element) {
        return;
    }

    element.textContent = message;
    element.classList.toggle(
        "error",
        isError
    );
}


async function fetchJson(
    endpoint,
    options = {}
) {
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers: {
                "Accept": "application/json",
                ...(options.headers || {}),
            },
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `API returned a non-JSON response (HTTP ${response.status}).`
        );
    }

    if (!response.ok) {
        const apiMessage =
            data?.error?.message ||
            `Request failed with HTTP ${response.status}.`;

        throw new Error(apiMessage);
    }

    return data;
}


async function checkApiHealth() {
    try {
        const data = await fetchJson(
            "/api/health"
        );

        if (
            data.success === true &&
            data.status === "healthy"
        ) {
            setApiStatus(
                true,
                "API connected"
            );

            return true;
        }

        setApiStatus(
            false,
            "API unavailable"
        );

        return false;
    } catch (error) {
        setApiStatus(
            false,
            "API unavailable"
        );

        return false;
    }
}


function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat(
        "en-IN"
    ).format(number);
}


function formatScore(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toFixed(1);
}


function getExposureLevel(score) {
    const value = Number(score);

    if (value <= 20) {
        return {
            label: "LOW",
            className: "exposure-low",
        };
    }

    if (value <= 40) {
        return {
            label: "MODERATE",
            className: "exposure-moderate",
        };
    }

    if (value <= 70) {
        return {
            label: "HIGH",
            className: "exposure-high",
        };
    }

    return {
        label: "CRITICAL",
        className: "exposure-critical",
    };
}


function humanizeCategory(category) {
    return String(category)
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) =>
            letter.toUpperCase()
        );
}


function renderSummaryCards(statistics) {
    const assessments =
        statistics.assessments || {};

    const categories =
        statistics.categories || {};

    const findings =
        statistics.findings || {};

    getElement(
        "total-assessments"
    ).textContent = formatNumber(
        assessments.total
    );

    getElement(
        "average-score"
    ).textContent = formatScore(
        assessments.average_score
    );

    getElement(
        "total-findings"
    ).textContent = formatNumber(
        findings.total
    );

    getElement(
        "category-count"
    ).textContent = formatNumber(
        categories.category_count
    );
}


function renderRiskDistributionChart(statistics) {
    const canvas = getElement(
        "risk-distribution-chart"
    );

    if (!canvas) {
        return;
    }

    const distribution =
        statistics.assessments
            ?.risk_distribution || {};

    const labels = [
        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL",
    ];

    const values = labels.map(
        (label) =>
            Number(
                distribution[label] || 0
            )
    );

    if (
        typeof Chart === "undefined"
    ) {
        return;
    }

    if (riskDistributionChart) {
        riskDistributionChart.destroy();
    }

    riskDistributionChart =
        new Chart(
            canvas,
            {
                type: "doughnut",
                data: {
                    labels,
                    datasets: [
                        {
                            label:
                                "Assessments",
                            data: values,
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                        },
                    },
                },
            }
        );
}


function renderCategoryScoreChart(statistics) {
    const canvas = getElement(
        "category-score-chart"
    );

    if (!canvas) {
        return;
    }

    const categoryScores =
        statistics.categories
            ?.average_scores || {};

    const entries = Object.entries(
        categoryScores
    );

    const labels = entries.map(
        ([category]) =>
            humanizeCategory(category)
    );

    const values = entries.map(
        ([, score]) =>
            Number(score)
    );

    if (
        typeof Chart === "undefined"
    ) {
        return;
    }

    if (categoryScoreChart) {
        categoryScoreChart.destroy();
    }

    categoryScoreChart =
        new Chart(
            canvas,
            {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        {
                            label:
                                "Average exposure score",
                            data: values,
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: "y",
                    scales: {
                        x: {
                            min: 0,
                            max: 100,
                            title: {
                                display: true,
                                text: "Score (0–100)",
                            },
                        },
                    },
                    plugins: {
                        legend: {
                            display: false,
                        },
                    },
                },
            }
        );
}


function renderCategoryTable(statistics) {
    const body = getElement(
        "category-table-body"
    );

    if (!body) {
        return;
    }

    const categoryScores =
        statistics.categories
            ?.average_scores || {};

    const entries = Object.entries(
        categoryScores
    ).sort(
        ([, first], [, second]) =>
            Number(second) - Number(first)
    );

    if (entries.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="3">
                    No category statistics available yet.
                </td>
            </tr>
        `;

        return;
    }

    body.innerHTML = entries
        .map(
            ([category, score]) => {
                const exposure =
                    getExposureLevel(
                        score
                    );

                return `
                    <tr>
                        <td>
                            ${humanizeCategory(category)}
                        </td>
                        <td>
                            <span class="score-pill">
                                ${formatScore(score)}
                            </span>
                        </td>
                        <td>
                            <span class="exposure-label ${exposure.className}">
                                ${exposure.label}
                            </span>
                        </td>
                    </tr>
                `;
            }
        )
        .join("");
}


async function loadDashboard() {
    setDashboardMessage(
        "Loading dashboard statistics..."
    );

    try {
        const data = await fetchJson(
            "/api/dashboard/stats"
        );

        if (
            data.success !== true ||
            !data.statistics
        ) {
            throw new Error(
                "Dashboard returned an unexpected response."
            );
        }

        renderSummaryCards(
            data.statistics
        );

        renderRiskDistributionChart(
            data.statistics
        );

        renderCategoryScoreChart(
            data.statistics
        );

        renderCategoryTable(
            data.statistics
        );

        setDashboardMessage(
            "Dashboard data loaded successfully."
        );
    } catch (error) {
        setDashboardMessage(
            error.message ||
                "Dashboard data could not be loaded.",
            true
        );

        const placeholders = [
            "total-assessments",
            "average-score",
            "total-findings",
            "category-count",
        ];

        placeholders.forEach(
            (id) => {
                const element =
                    getElement(id);

                if (element) {
                    element.textContent =
                        "—";
                }
            }
        );

        const body =
            getElement(
                "category-table-body"
            );

        if (body) {
            body.innerHTML = `
                <tr>
                    <td colspan="3">
                        Dashboard data is unavailable.
                        Start the Flask backend and refresh.
                    </td>
                </tr>
            `;
        }
    }
}


async function initializeApplication() {
    const isOnline =
        await checkApiHealth();

    if (isOnline) {
        await loadDashboard();
    } else {
        setDashboardMessage(
            "Backend API is unavailable. Start Flask and refresh the page.",
            true
        );
    }

    const refreshButton =
        getElement(
            "refresh-dashboard"
        );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            async () => {
                const online =
                    await checkApiHealth();

                if (online) {
                    await loadDashboard();
                }
            }
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);