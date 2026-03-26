document.addEventListener('DOMContentLoaded', () => {
    const clockElement = document.getElementById('clock');
    const timezoneSelect = document.getElementById('timezone');

    // Function to update the clock
    function updateClock() {
        const timezone = timezoneSelect.value;
        const options = { timeZone: timezone, hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
        const formatter = new Intl.DateTimeFormat([], options);
        const timeString = formatter.format(new Date());
        clockElement.textContent = timeString;
    }

    // Update the clock every second
    setInterval(updateClock, 1000);

    // Change event to update clock when timezone is changed
    timezoneSelect.addEventListener('change', updateClock);

    // Initial clock update
    updateClock();
});