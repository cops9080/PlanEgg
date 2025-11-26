document.addEventListener('DOMContentLoaded', () => {
    const dropdowns = document.querySelectorAll('.dropdown-wrapper');

    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');
        const items = dropdown.querySelectorAll('.dropdown-item');

        // Toggle dropdown
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close other dropdowns first
            dropdowns.forEach(d => {
                if (d !== dropdown) d.querySelector('.dropdown-menu').classList.remove('show');
            });
            menu.classList.toggle('show');
        });

        // Handle item selection
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                trigger.textContent = item.textContent + ' ▾';
                trigger.style.color = '#333'; // Active color
                menu.classList.remove('show');
                // Store the value
                dropdown.dataset.value = item.getAttribute('data-value');
            });
        });
    });

    // Close when clicking outside
    document.addEventListener('click', () => {
        dropdowns.forEach(dropdown => {
            dropdown.querySelector('.dropdown-menu').classList.remove('show');
        });
    });

    // Add Quest Button Logic
    const addButton = document.querySelector('.add_button');
    const questInput = document.querySelector('.textbox');
    const difficultyDropdown = document.getElementById('difficulty-dropdown');
    const timeDropdown = document.getElementById('time-dropdown');

    if (addButton) {
        addButton.addEventListener('click', () => {
            const questName = questInput.value.trim();
            const difficulty = difficultyDropdown.dataset.value;
            const time = timeDropdown.dataset.value;

            if (!questName) {
                alert('Please enter a quest name.');
                return;
            }
            if (!difficulty) {
                alert('Please select a difficulty.');
                return;
            }
            if (!time) {
                alert('Please select a time duration.');
                return;
            }

            fetch('/add_quest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    quest: questName,
                    difficulty: difficulty,
                    time: time
                }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        const message = `${data.message}\n(보상: ${data.coin} 코인, ${data.exp} 경험치)\n\n퀘스트 목록으로 이동하시겠습니까?`;
                        if (confirm(message)) {
                            window.location.href = '/questlist';
                        } else {
                            // Reset form
                            questInput.value = '';
                            difficultyDropdown.dataset.value = '';
                            difficultyDropdown.querySelector('.dropdown-trigger').textContent = 'Difficulty ▾';
                            difficultyDropdown.querySelector('.dropdown-trigger').style.color = '#555';

                            timeDropdown.dataset.value = '';
                            timeDropdown.querySelector('.dropdown-trigger').textContent = 'Time ▾';
                            timeDropdown.querySelector('.dropdown-trigger').style.color = '#555';
                        }
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert('An error occurred while adding the quest.');
                });
        });
    }
});
