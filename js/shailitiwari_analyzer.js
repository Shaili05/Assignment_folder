// starting with student data

const students = [
  {
    name: "Lalit",
    marks: [
      { subject: "Math", score: 78 },
      { subject: "English", score: 82 },
      { subject: "Science", score: 74 },
      { subject: "History", score: 69 },
      { subject: "Computer", score: 88 }
    ],
    attendance: 82
  },
  {
    name: "Rahul",
    marks: [
      { subject: "Math", score: 90 },
      { subject: "English", score: 85 },
      { subject: "Science", score: 80 },
      { subject: "History", score: 76 },
      { subject: "Computer", score: 92 }
    ],
    attendance: 91
  }
];

// calculating total marks for each student
function getTotalMarks(student) {
  let total = 0;

  // using loop to add all subject scores
  for (let i = 0; i < student.marks.length; i++) {
    total += student.marks[i].score;
  }

  return total;
}
// printing totals

students.forEach(stu => {
  console.log(stu.name + " Total Marks: " + getTotalMarks(stu));
});

// calculating average marks

function getAverage(student) {
  return (getTotalMarks(student) / student.marks.length).toFixed(1);
}

students.forEach(stu => {
  console.log(stu.name + " Average: " + getAverage(stu));
});

// finding highest score in each subject

function getHighestBySubject() {
  let highestMap = {};

  students.forEach(stu => {
    stu.marks.forEach(m => {
      if (!highestMap[m.subject] || m.score > highestMap[m.subject].score) {
        highestMap[m.subject] = {
          name: stu.name,
          score: m.score
        };
      }
    });
  });

  for (let subject in highestMap) {
    console.log(`Highest in ${subject}: ${highestMap[subject].name} (${highestMap[subject].score})`);
  }
}

getHighestBySubject();